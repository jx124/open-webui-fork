<script lang="ts">
	import { chats, showArchivedChats, showSettings, user, WEBUI_NAME } from '$lib/stores';
	import UserMenu from '$lib/components/layout/Sidebar/UserMenu.svelte';
	import { WEBUI_BASE_URL } from '$lib/constants';
	import { toast } from 'svelte-sonner';
	import SettingsModal from '$lib/components/chat/SettingsModal.svelte';
	import ArchivedChatsModal from '$lib/components/layout/Sidebar/ArchivedChatsModal.svelte';
	import { getChatList } from '$lib/apis/chats';
</script>

<svelte:head>
	<title>
		Classes | {$WEBUI_NAME}
	</title>
</svelte:head>

<SettingsModal bind:show={$showSettings} />
<ArchivedChatsModal
	bind:show={$showArchivedChats}
	on:change={async () => {
		$chats = await getChatList(localStorage.token).catch((error) => toast.error(error));
	}}
/>

<div class="app relative">
	<div
		class=" text-gray-700 dark:text-gray-100 bg-white dark:bg-gray-900 min-h-screen overflow-auto flex flex-row"
	>
		<div class="min-h-[calc(100dvh)] max-h-[calc(100dvh)] w-full max-w-full flex flex-col">
			<nav id="nav" class=" sticky py-2.5 top-0 flex flex-row justify-center z-30">
				<div
					class="px-2.5 flex items-center justify-between w-full max-w-full text-gray-600 dark:text-gray-400"
				>
					<div class="flex justify-between space-x-1 text-gray-600 dark:text-gray-400">
						<a
							id="sidebar-new-chat-button"
							class="flex flex-1 justify-between rounded-xl px-2 py-2 hover:bg-gray-100 dark:hover:bg-gray-850 transition"
							href="/"
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
								{$WEBUI_NAME}
							</div>
						</a>
					</div>

					<div
						class="self-start flex flex-none items-center space-x-0.5 md:space-x-1 text-gray-500 dark:text-gray-500"
					>
						<UserMenu
							className="max-w-[200px]"
							role={$user?.role}
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
										src={$user?.profile_image_url}
										class="size-6 object-cover rounded-full"
										alt="User profile"
										draggable="false"
									/>
								</div>
							</button>
						</UserMenu>
					</div>
				</div>
			</nav>
			<slot />
			
		</div>
	</div>
</div>

<style>
	.loading {
		display: inline-block;
		clip-path: inset(0 1ch 0 0);
		animation: l 1s steps(3) infinite;
		letter-spacing: -0.5px;
	}

	@keyframes l {
		to {
			clip-path: inset(0 -1ch 0 0);
		}
	}

	pre[class*='language-'] {
		position: relative;
		overflow: auto;

		/* make space  */
		margin: 5px 0;
		padding: 1.75rem 0 1.75rem 1rem;
		border-radius: 10px;
	}

	pre[class*='language-'] button {
		position: absolute;
		top: 5px;
		right: 5px;

		font-size: 0.9rem;
		padding: 0.15rem;
		background-color: #828282;

		border: ridge 1px #7b7b7c;
		border-radius: 5px;
		text-shadow: #c4c4c4 0 0 2px;
	}

	pre[class*='language-'] button:hover {
		cursor: pointer;
		background-color: #bcbabb;
	}
</style>
