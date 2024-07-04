<script lang="ts">
	import {
		WEBUI_NAME,
		chatId,
		chats,
		prompts,
		settings,
		showArchivedChats,
		showRightSidebar,
		showSidebar,
		user
	} from '$lib/stores';

	import ModelSelector from '../chat/ModelSelector.svelte';
	import PromptSelector from '../chat/PromptSelector.svelte';
	import UserMenu from './Sidebar/UserMenu.svelte';
	import MenuLines from '../icons/MenuLines.svelte';
	import { page } from '$app/stores';

	export let initNewChat: Function;
	export let title: string = $WEBUI_NAME;
	export let shareEnabled: boolean = false;

	export let chat;
	export let selectedModels;

	export let selectedPromptCommand: string;

	let evaluatedChat: null | string = null;
	let evaluatedChatTitle: string;

	$: {
		evaluatedChat = chat?.chat?.evaluatedChat ?? null;
		evaluatedChatTitle = $chats.find((chat) => chat?.id === evaluatedChat)?.title ?? "";
	}

	$: inChatInstance = $chatId !== '';

	$: if (!inChatInstance) {
		// Selecting prompt from main interface
		let prompt = $prompts.find((prompt) => prompt.command === selectedPromptCommand)?.content;
		$settings = {...$settings, system: prompt};
	} 

	export let showModelSelector = true;
</script>

<nav id="nav" class=" sticky py-2.5 top-0 flex flex-row justify-center z-30">
	<div class=" flex max-w-full w-full mx-auto px-5 pt-0.5 md:px-[1rem]">
		<div class="flex items-center justify-between w-full max-w-full">
			<div
				class="{$showSidebar
					? 'md:hidden'
					: ''} mr-3 self-start flex flex-none items-center text-gray-600 dark:text-gray-400"
			>
				<button
					id="sidebar-toggle-button"
					class="cursor-pointer px-2 py-2 flex rounded-xl hover:bg-gray-100 dark:hover:bg-gray-850 transition"
					on:click={() => {
						showSidebar.set(!$showSidebar);
					}}
				>
					<div class=" m-auto self-center">
						<MenuLines />
					</div>
				</button>
			</div>

			<div class="flex items-top w-full min-w-52">
				<div class="overflow-hidden max-w-full">
					{#if showModelSelector}
						<ModelSelector bind:selectedModels showSetDefault={!shareEnabled} />
					{/if}
				</div>

				<div class="overflow-hidden max-w-full">
					{#if evaluatedChat === null}
						<PromptSelector 
							bind:selectedPromptCommand
							bind:disabled={inChatInstance}
						/>
					{:else}
						<div class="flex w-full text-left px-0.5 space-x-1 outline-none bg-transparent truncate text-lg font-semibold placeholder-gray-400 focus:outline-none">
							<div>{"Evaluation for"}</div>
							<a href={"/c/" + evaluatedChat} class="hover:underline">{evaluatedChatTitle}</a>
						</div>
					{/if}
				</div>
			</div>

			<div class="self-start flex flex-none items-center text-gray-600 dark:text-gray-400">
				<div
					class="{$showRightSidebar
						? 'md:hidden'
						: ''} self-start flex flex-none items-center text-gray-500 dark:text-gray-500"
				>
					{#if inChatInstance}
						<button
							class=" cursor-pointer px-2 py-2 flex rounded-xl hover:bg-gray-100 dark:hover:bg-gray-850 transition"
							on:click={() => {
								showRightSidebar.set(!$showRightSidebar);
							}}
						>
							<div class=" m-auto self-center">
								<svg
									xmlns="http://www.w3.org/2000/svg"
									fill="none"
									viewBox="0 0 24 24"
									stroke-width="2"
									stroke="currentColor"
									class="size-5"
								>
									<path
										transform="scale(-1, 1)"
										transform-origin="center"
										stroke-linecap="round"
										stroke-linejoin="round"
										d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25H12"
									/>
								</svg>
							</div>
						</button>
					{/if}
					{#if $user !== undefined}
						<UserMenu
							className="max-w-[200px]"
							role={$user.role}
							on:show={(e) => {
								if (e.detail === 'archived-chat') {
									showArchivedChats.set(true);
								}
							}}
						>
							<button
								class="select-none flex rounded-xl p-1.5 w-full hover:bg-gray-100 dark:hover:bg-gray-850 transition"
								aria-label="User Menu"
							>
								<div class=" self-center">
									<img
										src={$user.profile_image_url}
										class="size-6 object-cover rounded-full"
										alt="User profile"
										draggable="false"
									/>
								</div>
							</button>
						</UserMenu>
					{/if}
				</div>
			</div>
		</div>
	</div>
</nav>
