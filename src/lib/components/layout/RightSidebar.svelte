<script lang="ts">
	import DownloadChatDropdown from "../chat/DownloadChatDropdown.svelte";
	import { chatId, prompts, showArchivedChats, showRightSidebar, user } from "$lib/stores";
	import UserMenu from "./Sidebar/UserMenu.svelte";
	import Menu from "./Navbar/Menu.svelte";
	import ShareChatModal from "../chat/ShareChatModal.svelte";
	import sanitizeHtml from 'sanitize-html';

    export let chat = null;
    let additionalInfo = null;

    $: if (chat) {
        additionalInfo = $prompts.find((prompt) => prompt.command === chat.chat.systemCommand)?.additional_info;

        if (chat.chat.evaluatedChat) {
            $showRightSidebar = false;
        }
    }

    $: if (additionalInfo) {
        // wait for main message component to load first
        setTimeout(() => {
            $showRightSidebar = true;
        }, 50);
    }
 
    let showShareChatModal = false;
	let showDownloadChatModal = false;

	export let shareEnabled: boolean = true;
</script>

<ShareChatModal bind:show={showShareChatModal} chatId={$chatId} />
<div
    id="right_sidebar"
    class="h-screen max-h-[100dvh] min-h-screen {$showRightSidebar
        ? 'md:relative w-[260px] lg:w-[400px]'
        : 'translate-x-[260px] lg:translate-x-[400px] w-[0px]'} bg-gray-50 text-gray-900 dark:bg-gray-950 dark:text-gray-200 text-sm transition fixed z-50 top-0 right-0 rounded-l-2xl"
>
    <div
    class="py-2.5 my-auto flex flex-col justify-start h-screen max-h-[100dvh] w-[260px] lg:w-[400px] z-50 {$showRightSidebar
        ? ''
        : 'invisible'}"
    >
        <div class="px-2.5 flex flex-row justify-between space-x-1 text-gray-600 dark:text-gray-400">
            <div class="flex">
                <button
                    class="self-start cursor-pointer px-2 py-2 flex rounded-xl hover:bg-gray-100 dark:hover:bg-gray-850 transition"
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
            </div>

            <div class="flex">
                <DownloadChatDropdown {chat} />
                <Menu
                    {chat}
                    {shareEnabled}
                    shareHandler={() => {
                        showShareChatModal = !showShareChatModal;
                    }}
                    downloadHandler={() => {
                        showDownloadChatModal = !showDownloadChatModal;
                    }}
                >
                    <button
                        class="flex cursor-pointer px-2 py-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-850 transition"
                        id="chat-context-menu-button"
                    >
                        <div class=" m-auto self-center">
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke-width="1.5"
                                stroke="currentColor"
                                class="size-5"
                            >
                                <path
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    d="M6.75 12a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0ZM12.75 12a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0ZM18.75 12a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0Z"
                                />
                            </svg>
                        </div>
                    </button>
                </Menu>
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

        <div class="flex flex-col m-2 overflow-hidden overscroll-contain">
            <div class="w-full pl-2.5 text-xs text-gray-500 dark:text-gray-500 font-medium">
                Additional Client Information
            </div>
            <div class="prose px-2.5 my-2 text-gray-600 dark:text-gray-400 overflow-y-auto whitespace-pre-line text-sm
                dark:prose-invert prose-headings:my-0 prose-p:my-0 prose-p:mb-0 prose-pre:my-0 prose-table:my-0 prose-blockquote:my-0 prose-img:my-0 prose-ul:-my-1 prose-ol:-my-1 prose-li:-my-1 prose-ul:-mb-3 prose-ol:-mb-3 prose-li:-mb-1">
                {#if additionalInfo}
                    {@html sanitizeHtml(additionalInfo)}
                {:else}
                    No additional information provided.
                {/if}
            </div>
        </div>
    </div>
</div>