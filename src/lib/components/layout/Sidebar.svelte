<script lang="ts">
	import {
		user,
		chats,
		chatId,
		showSidebar,
		mobile,
		showArchivedChats,
		classId,

		classes

	} from '$lib/stores';
	import { onMount } from 'svelte';

	import {
		getChatList,
	} from '$lib/apis/chats';
	import ShareChatModal from '../chat/ShareChatModal.svelte';
	import ArchivedChatsModal from './Sidebar/ArchivedChatsModal.svelte';
	import UserMenu from './Sidebar/UserMenu.svelte';
	import DocumentArrowUpSolid from '../icons/DocumentArrowUpSolid.svelte';
	import DocumentDuplicate from '../icons/DocumentDuplicate.svelte';
	import ChatBubbles from '../icons/ChatBubbles.svelte';

	const BREAKPOINT = 768;

	let navElement;

    let className = "";
	let shareChatId = null;
	let selectedChatId = null;

	let showShareChatModal = false;
	let showDropdown = false;

	mobile;

	onMount(async () => {
		mobile.subscribe((e) => {
			if ($showSidebar && e) {
				showSidebar.set(false);
			}

			if (!$showSidebar && !e) {
				showSidebar.set(true);
			}
		});

		showSidebar.set(window.innerWidth > BREAKPOINT);
		chats.set(await getChatList(localStorage.token));

		let touchstart;
		let touchend;

		function checkDirection() {
			const screenWidth = window.innerWidth;
			const swipeDistance = Math.abs(touchend.screenX - touchstart.screenX);
			if (touchstart.clientX < 40 && swipeDistance >= screenWidth / 8) {
				if (touchend.screenX < touchstart.screenX) {
					showSidebar.set(false);
				}
				if (touchend.screenX > touchstart.screenX) {
					showSidebar.set(true);
				}
			}
		}

		const onTouchStart = (e) => {
			touchstart = e.changedTouches[0];
			console.log(touchstart.clientX);
		};

		const onTouchEnd = (e) => {
			touchend = e.changedTouches[0];
			checkDirection();
		};

		window.addEventListener('touchstart', onTouchStart);
		window.addEventListener('touchend', onTouchEnd);

        if ($classId === null) {
            $classId = parseInt(localStorage.getItem("classId") ?? "0");
        }

        className = $classes.find((cls) => cls.id === $classId)?.name;

		return () => {
			window.removeEventListener('touchstart', onTouchStart);
			window.removeEventListener('touchend', onTouchEnd);
		};
	});

</script>

<ShareChatModal bind:show={showShareChatModal} chatId={shareChatId} />
<ArchivedChatsModal
	bind:show={$showArchivedChats}
	on:change={async () => {
		chats.set(await getChatList(localStorage.token));
	}}
/>

<!-- svelte-ignore a11y-no-static-element-interactions -->

{#if $showSidebar}
	<div
		class=" fixed md:hidden z-40 top-0 right-0 left-0 bottom-0 bg-black/60 w-full min-h-screen h-screen flex justify-center overflow-hidden overscroll-contain"
		on:mousedown={() => {
			showSidebar.set(!$showSidebar);
		}}
	/>
{/if}

<div
	bind:this={navElement}
	id="sidebar"
	class="h-screen max-h-[100dvh] min-h-screen select-none {$showSidebar
		? 'md:relative w-[260px]'
		: '-translate-x-[260px] w-[0px]'} bg-gray-50 text-gray-900 dark:bg-gray-950 dark:text-gray-200 text-sm transition fixed z-50 top-0 left-0 rounded-r-2xl
        "
	data-state={$showSidebar}
>
	<div
		class="py-2.5 my-auto flex flex-col justify-between h-screen max-h-[100dvh] w-[260px] z-50 {$showSidebar
			? ''
			: 'invisible'}"
	>
		<div class="px-2.5 flex justify-between space-x-1 text-gray-600 dark:text-gray-400">
            <div class="w-full">
                <div class="flex justify-between w-full space-x-1 text-gray-600 dark:text-gray-400 mb-4">
                    <a
                        id="assignment-button"
                        class="flex flex-1 rounded-xl px-2 py-2 hover:bg-gray-100 dark:hover:bg-gray-850 transition"
                        href="/classes/"
                        draggable="false"
                        on:click={() => {
                            $chatId = ""
                            $classId = null;
                        }}
                    >
                        <div class="self-center ml-1 mr-2 p-1 rounded-md text-gray-100 bg-gray-900 dark:text-gray-900 dark:bg-gray-100">
                            <ChatBubbles className={"size-5 stroke-current"} strokeWidth={"1.3"} />
                        </div>
                        <div class=" self-center text-gray-850 dark:text-white line-clamp-2 overflow-hidden text-ellipsis">
                            {className}
                        </div>
                    </a>
                </div>
                <div class="flex justify-between w-full space-x-1 text-gray-600 dark:text-gray-400">
                    <a
                        id="assignment-button"
                        class="flex flex-1 rounded-xl px-2 py-2 hover:bg-gray-100 dark:hover:bg-gray-850 transition"
                        href="/classes/{$classId}"
                        draggable="false"
                        on:click={() => $chatId = ""}
                    >
                        <div class="self-center mx-1.5">
                            <DocumentDuplicate />
                        </div>
                        <div class=" self-center text-sm text-gray-850 dark:text-white">
                            View Assignments
                        </div>
                    </a>
                </div>
                <div class="flex justify-between w-full space-x-1 text-gray-600 dark:text-gray-400">
                    <a
                        id="submission-button"
                        class="flex flex-1 rounded-xl px-2 py-2 hover:bg-gray-100 dark:hover:bg-gray-850 transition"
                        href="/classes/{$classId}/submissions"
                        draggable="false"
                        on:click={() => $chatId = ""}
                    >
                        <div class="self-center mx-1.5">
                            <DocumentArrowUpSolid />
                        </div>
                        <div class=" self-center text-sm text-gray-850 dark:text-white">
                            View Submissions
                        </div>
                    </a>
                </div>
                {#if $user?.role === 'admin' || $user?.role === 'instructor'}
                    <div class="flex justify-between w-full space-x-1 text-gray-600 dark:text-gray-400">
                        <a
                            class="flex flex-1 rounded-xl px-2 py-2 hover:bg-gray-100 dark:hover:bg-gray-850 transition"
                            href="/admin"
                            on:click={() => {
                                selectedChatId = null;
                                chatId.set('');
                            }}
                            draggable="false"
                        >
                            <div class="self-center mx-1.5">
                                <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                    stroke-width="2"
                                    stroke="currentColor"
                                    class="size-[1.1rem]"
                                >
                                    <path
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                        d="M13.5 16.875h3.375m0 0h3.375m-3.375 0V13.5m0 3.375v3.375M6 10.5h2.25a2.25 2.25 0 0 0 2.25-2.25V6a2.25 2.25 0 0 0-2.25-2.25H6A2.25 2.25 0 0 0 3.75 6v2.25A2.25 2.25 0 0 0 6 10.5Zm0 9.75h2.25A2.25 2.25 0 0 0 10.5 18v-2.25a2.25 2.25 0 0 0-2.25-2.25H6a2.25 2.25 0 0 0-2.25 2.25V18A2.25 2.25 0 0 0 6 20.25Zm9.75-9.75H18a2.25 2.25 0 0 0 2.25-2.25V6A2.25 2.25 0 0 0 18 3.75h-2.25A2.25 2.25 0 0 0 13.5 6v2.25a2.25 2.25 0 0 0 2.25 2.25Z"
                                    />
                                </svg>
                            </div>

                            <div class="flex self-center">
                                <div class=" self-center text-sm text-gray-850 dark:text-white">
                                    Admin Panel
                                </div>
                            </div>
                        </a>
                    </div>
                {/if}
            </div>
		</div>

		<div class="px-2.5">
			<!-- <hr class=" border-gray-900 mb-1 w-full" /> -->

			<div class="flex flex-col">
				{#if $user !== undefined}
					<UserMenu
						role={$user.role}
						on:show={(e) => {
							if (e.detail === 'archived-chat') {
								showArchivedChats.set(true);
							}
						}}
					>
						<button
							class=" flex rounded-xl py-3 px-3.5 w-full hover:bg-gray-100 dark:hover:bg-gray-900 transition"
							on:click={() => {
								showDropdown = !showDropdown;
							}}
						>
							<div class=" self-center mr-3">
								<img
									src={$user.profile_image_url}
									class=" max-w-[30px] object-cover rounded-full"
									alt="User profile"
								/>
							</div>
							<div class=" self-center font-semibold">{$user.name}</div>
						</button>
					</UserMenu>
				{/if}
			</div>
		</div>
	</div>
</div>

<style>
	.scrollbar-hidden:active::-webkit-scrollbar-thumb,
	.scrollbar-hidden:focus::-webkit-scrollbar-thumb,
	.scrollbar-hidden:hover::-webkit-scrollbar-thumb {
		visibility: visible;
	}
	.scrollbar-hidden::-webkit-scrollbar-thumb {
		visibility: hidden;
	}
</style>
