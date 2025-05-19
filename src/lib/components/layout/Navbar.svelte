<script lang="ts">
	import {
		chatId,
        classId,
        classes,
		prompts,
		selectedPromptCommand,
		settings,
		showArchivedChats,
		showSidebar,
		user,

		WEBUI_NAME

	} from '$lib/stores';

	import UserMenu from './Sidebar/UserMenu.svelte';
	import MenuLines from '../icons/MenuLines.svelte';
	import DownloadChatDropdown from '../chat/DownloadChatDropdown.svelte';
	import ChevronRight from '../icons/ChevronRight.svelte';
	import { page } from '$app/stores';
	import { WEBUI_BASE_URL } from '$lib/constants';

	export let chat;
	export let isSubmitted: boolean;

	$: inChatInstance = $chatId !== '';

	$: if (!inChatInstance) {
		// Selecting prompt from main interface
		let prompt = $prompts.find((prompt) => prompt.command === $selectedPromptCommand)?.content;
		$settings = {...$settings, system: prompt};
	}

    $: className = $classes.find((c) => c.id === $classId)?.name ?? "";
</script>

<nav id="nav" class=" sticky py-2.5 top-0 flex flex-row justify-center z-30">
	<div class=" flex max-w-full w-full mx-auto px-3 pt-0.5 md:px-[1rem]">
		<div class="flex items-center justify-between w-full max-w-full">
			<div
				class="mr-3 self-start flex flex-none items-center text-gray-600 dark:text-gray-400"
			>
                {#if !className}
                    <a
                        id="home-button"
                        class="flex flex-1 justify-between rounded-xl px-2 py-2 hover:bg-gray-100 dark:hover:bg-gray-850 transition"
                        href={$page.route.id === '/classes' ? '/' : '/classes'}
                        draggable="false"
                    >
                        <div class="self-center mx-1.5">
                            <img
                                crossorigin="anonymous"
                                src="{WEBUI_BASE_URL}/static/favicon.png"
                                class=" size-6 -translate-x-1.5 rounded-full"
                                alt="logo"
                            />
                        </div>
                        <div class=" self-center font-medium text-sm text-gray-850 dark:text-white">
                            {$page.route.id === '/classes' ? $WEBUI_NAME : "View Classes"}
                        </div>
                    </a>
                {:else}
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
                {/if}
			</div>
			
            <div class="flex items-center w-full text-sm min-w-52">
                {#if className}
                    <a class="dark:text-gray-500 text-gray-700 hover:dark:text-gray-200 hover:text-gray-700" href="/classes">
                        Classes
                    </a>
                    <ChevronRight className="w-3 h-3 mx-2" />
                    <a class="dark:text-gray-500 text-gray-500 dark:text-gray-700 hover:dark:text-gray-200 hover:text-gray-700" href="/classes/{$classId}">
                        {className}
                    </a>
                    {#if $page.url.pathname.split("/").at(-1) === "submissions"}
                        <ChevronRight className="w-3 h-3 mx-2" />
                        <a class="dark:text-gray-500 text-gray-500 dark:text-gray-700 hover:dark:text-gray-200 hover:text-gray-700" href="/classes/{$classId}/submissions">
                            Submissions
                        </a>
                    {:else}
                        <ChevronRight className="w-3 h-3 mx-2" />
                        <a class="dark:text-gray-500 text-gray-500 dark:text-gray-700 hover:dark:text-gray-200 hover:text-gray-700" href="/classes/{$classId}">
                            Assignments
                        </a>

                        {#if $page.params.prompt_id}
                            <ChevronRight className="w-3 h-3 mx-2" />
                            <a class="dark:text-gray-500 text-gray-500 dark:text-gray-700 hover:dark:text-gray-200 hover:text-gray-700" href="/classes/{$classId}/attempts/{$page.params.prompt_id}">
                                {$prompts.find((prompt) => prompt.id === parseInt($page.params.prompt_id))?.title} Attempts
                            </a>
                        {/if}
                    {/if}
                    {#if inChatInstance && chat}
                        <ChevronRight className="w-3 h-3 mx-2" />
                        <a class="dark:text-gray-500 text-gray-500 dark:text-gray-700 hover:dark:text-gray-200 hover:text-gray-700" href="/c/{$chatId}">
                            {chat.title}
                        </a>
                    {/if}
                {/if}
            </div>

			<div class="self-start flex flex-none items-center text-gray-600 dark:text-gray-400">
				<div
					class="self-start flex flex-none items-center space-x-0.5 md:space-x-1 text-gray-500 dark:text-gray-500"
				>
					{#if inChatInstance}
						<DownloadChatDropdown {chat} />
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
