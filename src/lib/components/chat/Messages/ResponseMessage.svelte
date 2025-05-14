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

	import { models, settings } from '$lib/stores';
	import {
		approximateToHumanReadable,
		revertSanitizedResponseContent,
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

	export let message;
	export let siblings;

	export let showPreviousMessage: Function;
	export let showNextMessage: Function;

	export let clientName;
	export let clientImage;

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

		<div class="w-full overflow-hidden pl-1">
			<Name>
				{message.role === "assistant" ? (clientName ?? "Client") : "Evaluation"}

				{#if message.timestamp}
					<span
						class=" self-center invisible group-hover:visible text-gray-400 text-xs font-medium uppercase"
					>
						{dayjs(message.timestamp * 1000).format($i18n.t('h:mm a'))}
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
