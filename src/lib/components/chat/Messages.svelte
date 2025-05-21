<script lang="ts">
	import { v4 as uuidv4 } from 'uuid';
	import { chats, settings, user as _user, mobile, prompts, classes, type Prompt, classId, selectedPromptCommand, chatId } from '$lib/stores';
	import { tick, getContext } from 'svelte';

	import { toast } from 'svelte-sonner';
	import { getChatList, submitChatById, updateChatById } from '$lib/apis/chats';

	import UserMessage from './Messages/UserMessage.svelte';
	import ResponseMessage from './Messages/ResponseMessage.svelte';
	import EvaluationMessage from './Messages/EvaluationMessage.svelte';
	import Placeholder from './Messages/Placeholder.svelte';
	import { copyToClipboard, findWordIndices } from '$lib/utils';
	import sanitizeHtml from 'sanitize-html';
	import ChevronUp from '../icons/ChevronUp.svelte';
	import ChevronDown from '../icons/ChevronDown.svelte';
	import { type Assignment } from '$lib/apis/classes';
	import SubmitChatModal from './SubmitChatModal.svelte';

	const i18n = getContext('i18n');

	export let sendPrompt: Function;

	export let user = $_user;
	export let prompt;
	export let bottomPadding = false;
	export let autoScroll;
	export let history = {};
	export let messages = [];

	export let selectedModels;
	export let selectedProfile: Prompt | undefined;
	export let showClientInfo = true;

	export let currentAssignment: Assignment | null = null;
	export let chatDisabled = false;
	export let isSubmitted = false;

	$: if (autoScroll && bottomPadding) {
		(async () => {
			await tick();
			scrollToBottom();
		})();
	}

	const scrollToBottom = () => {
		const element = document.getElementById('messages-container');
		element.scrollTop = element.scrollHeight;
	};

	const copyToClipboardWithToast = async (text) => {
		const res = await copyToClipboard(text);
		if (res) {
			toast.success($i18n.t('Copying to clipboard was successful!'));
		}
	};

	const confirmEditMessage = async (messageId, content) => {
		let userPrompt = content;
		let userMessageId = uuidv4();

		let userMessage = {
			id: userMessageId,
			parentId: history.messages[messageId].parentId,
			childrenIds: [],
			role: 'user',
			content: userPrompt,
			...(history.messages[messageId].files && { files: history.messages[messageId].files }),
			models: selectedModels.filter((m, mIdx) => selectedModels.indexOf(m) === mIdx)
		};

		let messageParentId = history.messages[messageId].parentId;

		if (messageParentId !== null) {
			history.messages[messageParentId].childrenIds = [
				...history.messages[messageParentId].childrenIds,
				userMessageId
			];
		}

		history.messages[userMessageId] = userMessage;
		history.currentId = userMessageId;

		await tick();
		await sendPrompt(userPrompt, userMessageId);
	};

	const updateChatMessages = async () => {
		await tick();
		await updateChatById(localStorage.token, $chatId, {
			messages: messages,
			history: history
		});

		await chats.set(await getChatList(localStorage.token));
	};

	const confirmEditResponseMessage = async (messageId, content) => {
		history.messages[messageId].originalContent = history.messages[messageId].content;
		history.messages[messageId].content = content;

		await updateChatMessages();
	};

	const rateMessage = async (messageId, rating) => {
		history.messages[messageId].annotation = {
			...history.messages[messageId].annotation,
			rating: rating
		};

		await updateChatMessages();
	};

	const showPreviousMessage = async (message) => {
		if (message.parentId !== null) {
			let messageId =
				history.messages[message.parentId].childrenIds[
					Math.max(history.messages[message.parentId].childrenIds.indexOf(message.id) - 1, 0)
				];

			if (message.id !== messageId) {
				let messageChildrenIds = history.messages[messageId].childrenIds;

				while (messageChildrenIds.length !== 0) {
					messageId = messageChildrenIds.at(-1);
					messageChildrenIds = history.messages[messageId].childrenIds;
				}

				history.currentId = messageId;
			}
		} else {
			let childrenIds = Object.values(history.messages)
				.filter((message) => message.parentId === null)
				.map((message) => message.id);
			let messageId = childrenIds[Math.max(childrenIds.indexOf(message.id) - 1, 0)];

			if (message.id !== messageId) {
				let messageChildrenIds = history.messages[messageId].childrenIds;

				while (messageChildrenIds.length !== 0) {
					messageId = messageChildrenIds.at(-1);
					messageChildrenIds = history.messages[messageId].childrenIds;
				}

				history.currentId = messageId;
			}
		}

		await tick();

		const element = document.getElementById('messages-container');
		autoScroll = element.scrollHeight - element.scrollTop <= element.clientHeight + 50;

		setTimeout(() => {
			scrollToBottom();
		}, 100);
	};

	const showNextMessage = async (message) => {
		if (message.parentId !== null) {
			let messageId =
				history.messages[message.parentId].childrenIds[
					Math.min(
						history.messages[message.parentId].childrenIds.indexOf(message.id) + 1,
						history.messages[message.parentId].childrenIds.length - 1
					)
				];

			if (message.id !== messageId) {
				let messageChildrenIds = history.messages[messageId].childrenIds;

				while (messageChildrenIds.length !== 0) {
					messageId = messageChildrenIds.at(-1);
					messageChildrenIds = history.messages[messageId].childrenIds;
				}

				history.currentId = messageId;
			}
		} else {
			let childrenIds = Object.values(history.messages)
				.filter((message) => message.parentId === null)
				.map((message) => message.id);
			let messageId =
				childrenIds[Math.min(childrenIds.indexOf(message.id) + 1, childrenIds.length - 1)];

			if (message.id !== messageId) {
				let messageChildrenIds = history.messages[messageId].childrenIds;

				while (messageChildrenIds.length !== 0) {
					messageId = messageChildrenIds.at(-1);
					messageChildrenIds = history.messages[messageId].childrenIds;
				}

				history.currentId = messageId;
			}
		}

		await tick();

		const element = document.getElementById('messages-container');
		autoScroll = element.scrollHeight - element.scrollTop <= element.clientHeight + 50;

		setTimeout(() => {
			scrollToBottom();
		}, 100);
	};

	const messageDeleteHandler = async (messageId) => {
		const messageToDelete = history.messages[messageId];
		const messageParentId = messageToDelete.parentId;
		const messageChildrenIds = messageToDelete.childrenIds ?? [];
		const hasSibling = messageChildrenIds.some(
			(childId) => history.messages[childId]?.childrenIds?.length > 0
		);
		messageChildrenIds.forEach((childId) => {
			const child = history.messages[childId];
			if (child && child.childrenIds) {
				if (child.childrenIds.length === 0 && !hasSibling) {
					// if last prompt/response pair
					history.messages[messageParentId].childrenIds = [];
					history.currentId = messageParentId;
				} else {
					child.childrenIds.forEach((grandChildId) => {
						if (history.messages[grandChildId]) {
							history.messages[grandChildId].parentId = messageParentId;
							history.messages[messageParentId].childrenIds.push(grandChildId);
						}
					});
				}
			}
			// remove response
			history.messages[messageParentId].childrenIds = history.messages[
				messageParentId
			].childrenIds.filter((id) => id !== childId);
		});
		// remove prompt
		history.messages[messageParentId].childrenIds = history.messages[
			messageParentId
		].childrenIds.filter((id) => id !== messageId);
		await updateChatById(localStorage.token, $chatId, {
			messages: messages,
			history: history
		});
	};
</script>

<div class="h-full flex flex-col">
	{#if selectedProfile}
		<div
			class="mx-auto w-full max-w-6xl px-6 lg:px-8 py-4 mb-4 border border-gray-200 dark:border-gray-600 rounded-lg"
		>
			<div class="flex flex-row items-center justify-between mb-2">
				<div class="flex text-2xl font-semibold items-center">
					Client Profile
				</div>
			</div>

			<div class="flex justify-start mb-4">
				<img
					src={selectedProfile.image_url ? selectedProfile.image_url : '/user.png'}
					alt="profile"
					class="rounded-full h-24 w-24 object-cover"
				/>
				<div class=" flex-1 self-center pl-3">
					<div class="text-xl font-bold">
						{selectedProfile.title}
					</div>
				</div>
			</div>

			<button
				type="button"
				class="flex hover:underline text-sm"
				on:click={() => {
					showClientInfo = !showClientInfo;
				}}
			>
				{showClientInfo ? 'Hide Client Information' : 'Show Client Information'}
				{#if showClientInfo}
					<ChevronUp className="self-center ml-2 size-3" strokeWidth={'2'} />
				{:else}
					<ChevronDown className="self-center ml-2 size-3" strokeWidth={'2'} />
				{/if}
			</button>

			{#if showClientInfo}
				<div
					class="w-full prose !max-w-none pt-4 text-gray-600 dark:text-gray-400 overflow-y-auto whitespace-pre-line text-sm
					dark:prose-invert prose-headings:my-0 prose-headings:-mb-2 prose-p:my-0 prose-p:mb-0 prose-pre:my-0 prose-table:my-0
					prose-blockquote:my-0 prose-img:my-0 prose-ul:-my-1 prose-ol:-my-1 prose-li:-my-1 prose-li:py-0.5
					prose-ul:-mb-3 prose-ol:-mb-3 prose-li:-mb-1"
				>
					{#if selectedProfile.additional_info}
						{@html sanitizeHtml(selectedProfile.additional_info)}
					{:else}
						No additional information provided.
					{/if}
				</div>
				<button
					type="button"
					class="flex hover:underline text-xs mt-2"
					on:click={() => {
						showClientInfo = false;
					}}
				>
					Hide
					<ChevronUp className="self-center ml-1 size-2" strokeWidth={'2'} />
				</button>
			{/if}
		</div>

		{#if $chatId === ""}
			<div class="mx-auto text:gray-500 dark:text-gray-400">
				Send a message to start a conversation with the client.
			</div>
		{/if}
	{/if}

	{#if $chatId === '' && !selectedProfile}
		<Placeholder
			modelIds={selectedModels}
			submitPrompt={async (p) => {
				let text = p;

				if (p.includes('{{CLIPBOARD}}')) {
					const clipboardText = await navigator.clipboard.readText().catch((err) => {
						toast.error($i18n.t('Failed to read clipboard contents'));
						return '{{CLIPBOARD}}';
					});

					text = p.replaceAll('{{CLIPBOARD}}', clipboardText);
				}

				prompt = text;

				await tick();

				const chatInputElement = document.getElementById('chat-textarea');
				if (chatInputElement) {
					prompt = p;

					chatInputElement.style.height = '';
					chatInputElement.style.height = Math.min(chatInputElement.scrollHeight, 200) + 'px';
					chatInputElement.focus();

					const words = findWordIndices(prompt);

					if (words.length > 0) {
						const word = words.at(0);
						chatInputElement.setSelectionRange(word?.startIndex, word.endIndex + 1);
					}
				}

				await tick();
			}}
		/>
	{:else}
		<div class="w-full pt-4">
			{#key $chatId}
				{#each messages as message, messageIdx}
					<div class=" w-full {messageIdx === messages.length - 1 ? ' pb-12' : ''}">
						<div
							class="flex flex-col justify-between px-5 mb-3 {$settings?.fullScreenMode ?? null
								? 'max-w-full'
								: 'max-w-5xl'} mx-auto rounded-lg group"
						>
							{#if message.role === 'user'}
								<UserMessage
									on:delete={() => messageDeleteHandler(message.id)}
									{user}
									{message}
									siblings={message.parentId !== null
										? history.messages[message.parentId]?.childrenIds ?? []
										: Object.values(history.messages)
												.filter((message) => message.parentId === null)
												.map((message) => message.id) ?? []}
									{confirmEditMessage}
									{showPreviousMessage}
									{showNextMessage}
								/>
							{:else if message.role === "assistant"}
								{#key message.id}
									<ResponseMessage
										{message}
										siblings={history.messages[message.parentId]?.childrenIds ?? []}
										{showPreviousMessage}
										{showNextMessage}
										clientName={selectedProfile?.title}
										clientImage={selectedProfile?.image_url}
										on:save={async (e) => {
											console.log('save', e);

											const message = e.detail;
											history.messages[message.id] = message;
											await updateChatById(localStorage.token, $chatId, {
												messages: messages,
												history: history
											});
										}}
									/>
								{/key}
                                {#if chatDisabled && messageIdx === (messages.length - 1)}
                                    <hr class="dark:border-gray-600 border-gray-700 mt-3"/>
                                    <div class="flex justify-center text-sm mt-2 mb-4 dark:text-gray-500 text-gray-700">Conversation ended, you cannot send any more messages.</div>
                                {/if}
                            {:else}
                                <hr class="dark:border-gray-600 border-gray-700"/>
                                <div class="flex justify-center text-sm mt-2 mb-4 dark:text-gray-500 text-gray-700">Conversation ended, you cannot send any more messages.</div>
                                <div class="bg-sky-50 dark:bg-sky-950 p-5 rounded-lg">
                                    <EvaluationMessage
                                        {message}
                                        siblings={history.messages[message.parentId]?.childrenIds ?? []}
                                        {showPreviousMessage}
                                        {showNextMessage}
                                        {copyToClipboardWithToast}
                                        on:save={async (e) => {
                                            console.log('save', e);

                                            const message = e.detail;
                                            history.messages[message.id] = message;
                                            await updateChatById(localStorage.token, $chatId, {
                                                messages: messages,
                                                history: history
                                            });
                                        }}
                                    />
                                </div>
							{/if}
						</div>
					</div>
				{/each}


				{#if bottomPadding}
					<div class="  pb-20" />
				{/if}
			{/key}
		</div>
	{/if}
</div>
