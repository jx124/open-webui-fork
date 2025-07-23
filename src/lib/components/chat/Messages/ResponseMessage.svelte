<script lang="ts">
	import { toast } from 'svelte-sonner';
	import dayjs from 'dayjs';
	import { marked } from 'marked';
	import tippy from 'tippy.js';
	import auto_render from 'katex/dist/contrib/auto-render.mjs';
	import 'katex/dist/katex.min.css';
	import mermaid from 'mermaid';

	import { createEventDispatcher } from 'svelte';
	import { onMount, tick, getContext } from 'svelte';

	const i18n = getContext('i18n');

	const dispatch = createEventDispatcher();

	import { models, settings, type AudioSettings } from '$lib/stores';
	import {
		approximateToHumanReadable,
		revertSanitizedResponseContent,
        extractSentences,
		sanitizeResponseContent
	} from '$lib/utils';
	import { WEBUI_BASE_URL } from '$lib/constants';

	import Name from './Name.svelte';
	import ProfileImage from './ProfileImage.svelte';
	import Skeleton from './Skeleton.svelte';
	import CodeBlock from './CodeBlock.svelte';
	import Image from '$lib/components/common/Image.svelte';
	import CitationsModal from '$lib/components/chat/Messages/CitationsModal.svelte';
	import Spinner from '$lib/components/common/Spinner.svelte';
	import WebSearchResults from './ResponseMessage/WebSearchResults.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import { synthesizeOpenAISpeech, synthesizeElevenLabsSpeech } from '$lib/apis/audio';

	export let message;
	export let siblings;

	export let showPreviousMessage: Function;
	export let showNextMessage: Function;

	export let clientName;
	export let clientImage;

    export let isLastMessage = true;
    export let audio: AudioSettings | null;

	let loadingSpeech = false;
	let sentencesAudio = {};
	let speaking = false;
	let speakingIdx = null;

	let model = null;
	$: model = $models.find((m) => m.id === message.model);

	let tooltipInstance = null;

	let showCitationModal = false;

	let selectedCitation = null;

	$: tokens = marked.lexer(sanitizeResponseContent(message?.content));

	const renderer = new marked.Renderer();

	// For code blocks with simple backticks
	renderer.codespan = (code) => {
		return `<code>${code.replaceAll('&amp;', '&')}</code>`;
	};

	// Open all links in a new tab/window (from https://github.com/markedjs/marked/issues/655#issuecomment-383226346)
	const origLinkRenderer = renderer.link;
	renderer.link = (href, title, text) => {
		const html = origLinkRenderer.call(renderer, href, title, text);
		return html.replace(/^<a /, '<a target="_blank" rel="nofollow" ');
	};

	const { extensions, ...defaults } = marked.getDefaults() as marked.MarkedOptions & {
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		extensions: any;
	};

	$: if (message) {
		renderStyling();
	}

	const renderStyling = async () => {
		await tick();

		if (tooltipInstance) {
			tooltipInstance[0]?.destroy();
		}

		renderLatex();

		if (message.info) {
			let tooltipContent = '';
			if (message.info.openai) {
				tooltipContent = `prompt_tokens: ${message.info.prompt_tokens ?? 'N/A'}<br/>
													completion_tokens: ${message.info.completion_tokens ?? 'N/A'}<br/>
													total_tokens: ${message.info.total_tokens ?? 'N/A'}`;
			} else {
				tooltipContent = `response_token/s: ${
					`${
						Math.round(
							((message.info.eval_count ?? 0) / (message.info.eval_duration / 1000000000)) * 100
						) / 100
					} tokens` ?? 'N/A'
				}<br/>
					prompt_token/s: ${
						Math.round(
							((message.info.prompt_eval_count ?? 0) /
								(message.info.prompt_eval_duration / 1000000000)) *
								100
						) / 100 ?? 'N/A'
					} tokens<br/>
                    total_duration: ${
											Math.round(((message.info.total_duration ?? 0) / 1000000) * 100) / 100 ??
											'N/A'
										}ms<br/>
                    load_duration: ${
											Math.round(((message.info.load_duration ?? 0) / 1000000) * 100) / 100 ?? 'N/A'
										}ms<br/>
                    prompt_eval_count: ${message.info.prompt_eval_count ?? 'N/A'}<br/>
                    prompt_eval_duration: ${
											Math.round(((message.info.prompt_eval_duration ?? 0) / 1000000) * 100) /
												100 ?? 'N/A'
										}ms<br/>
                    eval_count: ${message.info.eval_count ?? 'N/A'}<br/>
                    eval_duration: ${
											Math.round(((message.info.eval_duration ?? 0) / 1000000) * 100) / 100 ?? 'N/A'
										}ms<br/>
                    approximate_total: ${approximateToHumanReadable(message.info.total_duration)}`;
			}
			tooltipInstance = tippy(`#info-${message.id}`, {
				content: `<span class="text-xs" id="tooltip-${message.id}">${tooltipContent}</span>`,
				allowHTML: true
			});
		}
	};

	const renderLatex = () => {
		let chatMessageElements = document
			.getElementById(`message-${message.id}`)
			?.getElementsByClassName('chat-assistant');

		if (chatMessageElements) {
			for (const element of chatMessageElements) {
				auto_render(element, {
					// customised options
					// • auto-render specific keys, e.g.:
					delimiters: [
						{ left: '$$', right: '$$', display: false },
						{ left: '$ ', right: ' $', display: false },
						{ left: '\\(', right: '\\)', display: false },
						{ left: '\\[', right: '\\]', display: false },
						{ left: '[ ', right: ' ]', display: false }
					],
					// • rendering keys, e.g.:
					throwOnError: false
				});
			}
		}
	};

	const playAudio = (idx) => {
		return new Promise((res) => {
			speakingIdx = idx;
			const audio = sentencesAudio[idx];
			audio.play();
			audio.onended = async (e) => {
				await new Promise((r) => setTimeout(r, 300));

				if (Object.keys(sentencesAudio).length - 1 === idx) {
					speaking = false;

					if ($settings.conversationMode) {
						document.getElementById('voice-input-button')?.click();
					}
				}

				res(e);
			};
		});
	};

	const toggleSpeakMessage = async () => {
		if (speaking) {
			try {
				speechSynthesis.cancel();

				sentencesAudio[speakingIdx].pause();
				sentencesAudio[speakingIdx].currentTime = 0;
			} catch {}

			speaking = false;
			speakingIdx = null;
		} else {
			speaking = true;

			if (audio?.TTSEngine === 'openai') {
				loadingSpeech = true;

				const sentences = extractSentences(message.content).reduce((mergedTexts, currentText) => {
					const lastIndex = mergedTexts.length - 1;
					if (lastIndex >= 0) {
						const previousText = mergedTexts[lastIndex];
						const wordCount = previousText.split(/\s+/).length;
						if (wordCount < 2) {
							mergedTexts[lastIndex] = previousText + ' ' + currentText;
						} else {
							mergedTexts.push(currentText);
						}
					} else {
						mergedTexts.push(currentText);
					}
					return mergedTexts;
				}, []);

				console.log(sentences);

				sentencesAudio = sentences.reduce((a, e, i, arr) => {
					a[i] = null;
					return a;
				}, {});

				let lastPlayedAudioPromise = Promise.resolve(); // Initialize a promise that resolves immediately

				for (const [idx, sentence] of sentences.entries()) {
					const res = await synthesizeOpenAISpeech(
						localStorage.token,
						audio?.speaker,
						sentence,
						audio?.model
					).catch((error) => {
						toast.error(error);

						speaking = false;
						loadingSpeech = false;

						return null;
					});

					if (res) {
						const blob = await res.blob();
						const blobUrl = URL.createObjectURL(blob);
						const audio = new Audio(blobUrl);
						sentencesAudio[idx] = audio;
						loadingSpeech = false;
						lastPlayedAudioPromise = lastPlayedAudioPromise.then(() => playAudio(idx));
					}
				}
            } else if (audio?.TTSEngine === "elevenlabs") {
                sentencesAudio[0] = null;
				let lastPlayedAudioPromise = Promise.resolve(); // Initialize a promise that resolves immediately

                const res = await synthesizeElevenLabsSpeech(
                    localStorage.token,
                    audio?.speaker,
                    message.content,
                    audio?.model
                ).catch((error) => {
                    toast.error(error);

                    speaking = false;
                    loadingSpeech = false;

                    return null;
                });

                if (res) {
                    const blob = await res.blob();
                    const blobUrl = URL.createObjectURL(blob);
                    const audio = new Audio(blobUrl);
                    sentencesAudio[0] = audio;
                    loadingSpeech = false;
                    lastPlayedAudioPromise = lastPlayedAudioPromise.then(() => playAudio(0));
                }
			} else {
				let voices = [];
				const getVoicesLoop = setInterval(async () => {
					voices = speechSynthesis.getVoices();
					if (voices.length > 0) {
						clearInterval(getVoicesLoop);

						const voice =
							voices?.filter((v) => v.name === audio?.speaker)?.at(0) ?? undefined;

						const speak = new SpeechSynthesisUtterance(message.content);

						speak.onend = () => {
							speaking = false;
							if ($settings.conversationMode) {
								document.getElementById('voice-input-button')?.click();
							}
						};
						speak.voice = voice;
						speechSynthesis.speak(speak);
					}
				}, 100);
			}
		}
	};

	onMount(async () => {
		await tick();
		renderStyling();

		await mermaid.run({
			querySelector: '.mermaid'
		});
	});
</script>

<CitationsModal bind:show={showCitationModal} citation={selectedCitation} />

{#key message.id}
	<div
		class=" flex w-full message-{message.id}"
		id="message-{message.id}"
		dir={$settings.chatDirection}
	>
        {#if message.role === "assistant"}
            <ProfileImage
                src={clientImage ? clientImage : `/user.png`}
            />
        {/if}

		<div class="w-full overflow-hidden pl-1 text-gray-800 dark:text-gray-100">
			<Name>
				{message.role === "assistant" ? (clientName ?? "Client") : "Evaluation"}

				{#if message.timestamp}
					<span
						class=" self-center text-gray-400 text-xs font-medium"
					>
						{dayjs(message.timestamp * 1000).format($i18n.t('MMM DD, h:mm A'))}
					</span>
				{/if}
			</Name>

			{#if (message?.files ?? []).filter((f) => f.type === 'image').length > 0}
				<div class="my-2.5 w-full flex overflow-x-auto gap-2 flex-wrap">
					{#each message.files as file}
						<div>
							{#if file.type === 'image'}
								<Image src={file.url} />
							{/if}
						</div>
					{/each}
				</div>
			{/if}

			<div
				class="prose chat-{message.role} w-full max-w-full dark:prose-invert prose-headings:my-0 prose-headings:-mb-4 prose-p:m-0 prose-p:-mb-6 prose-pre:my-0 prose-table:my-0 prose-blockquote:my-0 prose-img:my-0 prose-ul:-my-4 prose-ol:-my-4 prose-li:-my-3 prose-ul:-mb-6 prose-ol:-mb-8 prose-ol:p-0 prose-li:-mb-4 whitespace-pre-line"
			>
				<div>
					{#if message?.status}
						<div class="flex items-center gap-2 pt-1 pb-1">
							{#if message?.status?.done === false}
								<div class="">
									<Spinner className="size-4" />
								</div>
							{/if}

							{#if message?.status?.action === 'web_search' && message?.status?.urls}
								<WebSearchResults urls={message?.status?.urls}>
									<div class="flex flex-col justify-center -space-y-0.5">
										<div class="text-base line-clamp-1 text-wrap">
											{message.status.description}
										</div>
									</div>
								</WebSearchResults>
							{:else}
								<div class="flex flex-col justify-center -space-y-0.5">
									<div class=" text-gray-500 dark:text-gray-500 text-base line-clamp-1 text-wrap">
										{message.status.description}
									</div>
								</div>
							{/if}
						</div>
					{/if}

                    <div class="w-full">
                        {#if message.content === '' && !message.error}
                            <Skeleton />
                        {:else if message.content && message.error !== true}
                            <!-- always show message contents even if there's an error -->
                            <!-- unless message.error === true which is legacy error handling, where the error message is stored in message.content -->
                            {#each tokens as token, tokenIdx}
                                {#if token.type === 'code'}
                                    {#if token.lang === 'mermaid'}
                                        <pre class="mermaid">{revertSanitizedResponseContent(token.text)}</pre>
                                    {:else}
                                        <CodeBlock
                                            id={`${message.id}-${tokenIdx}`}
                                            lang={token?.lang ?? ''}
                                            code={revertSanitizedResponseContent(token?.text ?? '')}
                                        />
                                    {/if}
                                {:else}
                                    {@html marked.parse(token.raw, {
                                        ...defaults,
                                        gfm: true,
                                        breaks: true,
                                        renderer
                                    })}
                                {/if}
                            {/each}
                        {/if}

                        {#if message.error}
                            <div
                                class="flex mt-2 mb-4 space-x-2 border px-4 py-3 border-red-800 bg-red-800/30 font-medium rounded-lg"
                            >
                                <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                    stroke-width="1.5"
                                    stroke="currentColor"
                                    class="w-5 h-5 self-center"
                                >
                                    <path
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                        d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z"
                                    />
                                </svg>

                                <div class=" self-center">
                                    {message?.error?.content ?? message.content}
                                </div>
                            </div>
                        {/if}

                        {#if message.citations}
                            <div class="mt-1 mb-2 w-full flex gap-1 items-center flex-wrap">
                                {#each message.citations.reduce((acc, citation) => {
                                    citation.document.forEach((document, index) => {
                                        const metadata = citation.metadata?.[index];
                                        const id = metadata?.source ?? 'N/A';
                                        let source = citation?.source;
                                        // Check if ID looks like a URL
                                        if (id.startsWith('http://') || id.startsWith('https://')) {
                                            source = { name: id };
                                        }

                                        const existingSource = acc.find((item) => item.id === id);

                                        if (existingSource) {
                                            existingSource.document.push(document);
                                            existingSource.metadata.push(metadata);
                                        } else {
                                            acc.push( { id: id, source: source, document: [document], metadata: metadata ? [metadata] : [] } );
                                        }
                                    });
                                    return acc;
                                }, []) as citation, idx}
                                    <div class="flex gap-1 text-xs font-semibold">
                                        <button
                                            class="flex dark:text-gray-300 py-1 px-1 bg-gray-50 hover:bg-gray-100 dark:bg-gray-850 dark:hover:bg-gray-800 transition rounded-xl"
                                            on:click={() => {
                                                showCitationModal = true;
                                                selectedCitation = citation;
                                            }}
                                        >
                                            <div class="bg-white dark:bg-gray-700 rounded-full size-4">
                                                {idx + 1}
                                            </div>
                                            <div class="flex-1 mx-2 line-clamp-1">
                                                {citation.source.name}
                                            </div>
                                        </button>
                                    </div>
                                {/each}
                            </div>
                        {/if}

                        {#if message.done || siblings.length > 1}
                            <div
                                class=" flex justify-start overflow-x-auto buttons text-gray-600 dark:text-gray-500"
                            >
                                {#if siblings.length > 1}
                                    <div class="flex self-center min-w-fit" dir="ltr">
                                        <button
                                            class="self-center p-1 hover:bg-black/5 dark:hover:bg-white/5 dark:hover:text-white hover:text-black rounded-md transition"
                                            on:click={() => {
                                                showPreviousMessage(message);
                                            }}
                                        >
                                            <svg
                                                xmlns="http://www.w3.org/2000/svg"
                                                fill="none"
                                                viewBox="0 0 24 24"
                                                stroke="currentColor"
                                                stroke-width="2.5"
                                                class="size-3.5"
                                            >
                                                <path
                                                    stroke-linecap="round"
                                                    stroke-linejoin="round"
                                                    d="M15.75 19.5 8.25 12l7.5-7.5"
                                                />
                                            </svg>
                                        </button>

                                        <div
                                            class="text-sm tracking-widest font-semibold self-center dark:text-gray-100 min-w-fit"
                                        >
                                            {siblings.indexOf(message.id) + 1}/{siblings.length}
                                        </div>

                                        <button
                                            class="self-center p-1 hover:bg-black/5 dark:hover:bg-white/5 dark:hover:text-white hover:text-black rounded-md transition"
                                            on:click={() => {
                                                showNextMessage(message);
                                            }}
                                        >
                                            <svg
                                                xmlns="http://www.w3.org/2000/svg"
                                                fill="none"
                                                viewBox="0 0 24 24"
                                                stroke="currentColor"
                                                stroke-width="2.5"
                                                class="size-3.5"
                                            >
                                                <path
                                                    stroke-linecap="round"
                                                    stroke-linejoin="round"
                                                    d="m8.25 4.5 7.5 7.5-7.5 7.5"
                                                />
                                            </svg>
                                        </button>
                                    </div>
                                {/if}

                                {#if message.done && audio}
                                    <Tooltip content={$i18n.t('Read Aloud')} placement="bottom">
                                        <button
                                            id="speak-button-{message.id}"
                                            class="{isLastMessage
                                                ? 'visible'
                                                : 'invisible group-hover:visible'} p-1.5 hover:bg-black/5 dark:hover:bg-white/5 rounded-lg dark:hover:text-white hover:text-black transition"
                                            on:click={() => {
                                                if (!loadingSpeech) {
                                                    toggleSpeakMessage();
                                                }
                                            }}
                                        >
                                            {#if loadingSpeech}
                                                <svg
                                                    class=" w-4 h-4"
                                                    fill="currentColor"
                                                    viewBox="0 0 24 24"
                                                    xmlns="http://www.w3.org/2000/svg"
                                                    ><style>
                                                        .spinner_S1WN {
                                                            animation: spinner_MGfb 0.8s linear infinite;
                                                            animation-delay: -0.8s;
                                                        }
                                                        .spinner_Km9P {
                                                            animation-delay: -0.65s;
                                                        }
                                                        .spinner_JApP {
                                                            animation-delay: -0.5s;
                                                        }
                                                        @keyframes spinner_MGfb {
                                                            93.75%,
                                                            100% {
                                                                opacity: 0.2;
                                                            }
                                                        }
                                                    </style><circle class="spinner_S1WN" cx="4" cy="12" r="3" /><circle
                                                        class="spinner_S1WN spinner_Km9P"
                                                        cx="12"
                                                        cy="12"
                                                        r="3"
                                                    /><circle
                                                        class="spinner_S1WN spinner_JApP"
                                                        cx="20"
                                                        cy="12"
                                                        r="3"
                                                    /></svg
                                                >
                                            {:else if speaking}
                                                <svg
                                                    xmlns="http://www.w3.org/2000/svg"
                                                    fill="none"
                                                    viewBox="0 0 24 24"
                                                    stroke-width="2.3"
                                                    stroke="currentColor"
                                                    class="w-4 h-4"
                                                >
                                                    <path
                                                        stroke-linecap="round"
                                                        stroke-linejoin="round"
                                                        d="M17.25 9.75 19.5 12m0 0 2.25 2.25M19.5 12l2.25-2.25M19.5 12l-2.25 2.25m-10.5-6 4.72-4.72a.75.75 0 0 1 1.28.53v15.88a.75.75 0 0 1-1.28.53l-4.72-4.72H4.51c-.88 0-1.704-.507-1.938-1.354A9.009 9.009 0 0 1 2.25 12c0-.83.112-1.633.322-2.396C2.806 8.756 3.63 8.25 4.51 8.25H6.75Z"
                                                    />
                                                </svg>
                                            {:else}
                                                <svg
                                                    xmlns="http://www.w3.org/2000/svg"
                                                    fill="none"
                                                    viewBox="0 0 24 24"
                                                    stroke-width="2.3"
                                                    stroke="currentColor"
                                                    class="w-4 h-4"
                                                >
                                                    <path
                                                        stroke-linecap="round"
                                                        stroke-linejoin="round"
                                                        d="M19.114 5.636a9 9 0 010 12.728M16.463 8.288a5.25 5.25 0 010 7.424M6.75 8.25l4.72-4.72a.75.75 0 011.28.53v15.88a.75.75 0 01-1.28.53l-4.72-4.72H4.51c-.88 0-1.704-.507-1.938-1.354A9.01 9.01 0 012.25 12c0-.83.112-1.633.322-2.396C2.806 8.756 3.63 8.25 4.51 8.25H6.75z"
                                                    />
                                                </svg>
                                            {/if}
                                        </button>
                                    </Tooltip>
                                {/if}
                            </div>
                        {/if}
                    </div>
				</div>
			</div>
		</div>
	</div>
{/key}

<style>
	.buttons::-webkit-scrollbar {
		display: none; /* for Chrome, Safari and Opera */
	}

	.buttons {
		-ms-overflow-style: none; /* IE and Edge */
		scrollbar-width: none; /* Firefox */
	}
</style>
