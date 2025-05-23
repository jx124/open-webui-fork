<script lang="ts">
	import { onMount, tick, getContext } from 'svelte';
	import { openDB, deleteDB } from 'idb';
	import fileSaver from 'file-saver';
	const { saveAs } = fileSaver;

	import { goto } from '$app/navigation';

	import { getModels as _getModels } from '$lib/apis';
	import { getPrompts } from '$lib/apis/prompts';

	import { getDocs } from '$lib/apis/documents';
	import { getAllChatTags } from '$lib/apis/chats';

	import {
		user,
		showSettings,
		settings,
		models,
		prompts,
		documents,
		tags,
		banners,
		showChangelog,
		config,

		classes

	} from '$lib/stores';

	import SettingsModal from '$lib/components/chat/SettingsModal.svelte';
	import Sidebar from '$lib/components/layout/Sidebar.svelte';
	import ShortcutsModal from '$lib/components/chat/ShortcutsModal.svelte';
	import ChangelogModal from '$lib/components/ChangelogModal.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import { getBanners } from '$lib/apis/configs';
	import { getUserSettings } from '$lib/apis/users';
	import { getClassList } from '$lib/apis/classes';
	import { page } from '$app/stores';

	const i18n = getContext('i18n');

	let ollamaVersion = '';
	let loaded = false;
	let showShortcutsButtonElement: HTMLButtonElement;
	let DB = null;
	let localDBChats = [];

	let showShortcuts = false;

	const getModels = async () => {
		return _getModels(localStorage.token);
	};

	onMount(async () => {
		if ($user === undefined) {
			await goto('/auth');
		} else if ($user.role !== "pending") {
			try {
				// Check if IndexedDB exists
				DB = await openDB('Chats', 1);

				if (DB) {
					const chats = await DB.getAllFromIndex('chats', 'timestamp');
					localDBChats = chats.map((item, idx) => chats[chats.length - 1 - idx]);

					if (localDBChats.length === 0) {
						await deleteDB('Chats');
					}
				}

				console.log(DB);
			} catch (error) {
				// IndexedDB Not Found
			}

			const userSettings = await getUserSettings(localStorage.token);

			if (userSettings) {
				await settings.set(userSettings.ui);
			} else {
				await settings.set(JSON.parse(localStorage.getItem('settings') ?? '{}'));
			}

			await Promise.all([
				(async () => {
					models.set(await getModels());
				})(),
				(async () => {
					prompts.set(await getPrompts(localStorage.token));
				})(),
				(async () => {
					documents.set(await getDocs(localStorage.token));
				})(),
				(async () => {
					banners.set(await getBanners(localStorage.token));
				})(),
				(async () => {
					tags.set(await getAllChatTags(localStorage.token));
				})(),
				(async () => {
					classes.set(await getClassList(localStorage.token));
				})(),
			]);

			document.addEventListener('keydown', function (event) {
				const isCtrlPressed = event.ctrlKey || event.metaKey; // metaKey is for Cmd key on Mac
				// Check if the Shift key is pressed
				const isShiftPressed = event.shiftKey;

				// Check if Shift + Esc is pressed
				if (isShiftPressed && event.key === 'Escape') {
					event.preventDefault();
					console.log('focusInput');
					document.getElementById('chat-textarea')?.focus();
				}

				// Check if Ctrl + Shift + S is pressed
				if (isCtrlPressed && isShiftPressed && event.key.toLowerCase() === 's') {
					event.preventDefault();
					console.log('toggleSidebar');
					document.getElementById('sidebar-toggle-button')?.click();
				}

				// Check if Ctrl + Shift + Backspace is pressed
				if (isCtrlPressed && isShiftPressed && event.key === 'Backspace') {
					event.preventDefault();
					console.log('deleteChat');
					document.getElementById('delete-chat-button')?.click();
				}

				// Check if Ctrl + / is pressed
				if (isCtrlPressed && event.key === '/') {
					event.preventDefault();
					console.log('showShortcuts');
					showShortcutsButtonElement.click();
				}
			});

			if ($user.role === 'admin') {
				showChangelog.set(localStorage.version !== $config.version);
			}

			await tick();

			if (['admin', 'instructor'].includes($user?.role ?? '')) {
                if ($classes.length === 0) {
                    await goto("/admin")
                }
			} 
            if (!$page.url.pathname.startsWith("/c/") && !$page.url.pathname.startsWith("/admin")) {
                await goto('/classes');
            }
		}

		loaded = true;
	});
</script>

<div class=" hidden lg:flex fixed bottom-0 right-0 px-2 py-2 z-10">
	<Tooltip content={$i18n.t('Help')} placement="left">
		<button
			id="show-shortcuts-button"
			bind:this={showShortcutsButtonElement}
			class="text-gray-600 dark:text-gray-300 bg-gray-300/20 size-5 flex items-center justify-center text-[0.7rem] rounded-full"
			on:click={() => {
				showShortcuts = !showShortcuts;
			}}
		>
			?
		</button>
	</Tooltip>
</div>

<ShortcutsModal bind:show={showShortcuts} />
<SettingsModal bind:show={$showSettings} />
<ChangelogModal bind:show={$showChangelog} />

<div class="app relative">
	<div
		class=" text-gray-700 dark:text-gray-100 bg-white dark:bg-gray-900 min-h-screen overflow-auto flex flex-row"
	>
		{#if loaded}
			{#if ["pending"].includes($user.role)}
				<div class="fixed w-full h-full flex z-[999]">
					<div
						class="absolute w-full h-full backdrop-blur-lg bg-white/10 dark:bg-gray-900/50 flex justify-center"
					>
						<div class="m-auto pb-10 flex flex-col justify-center">
							<div class="max-w-md">
								<div class="text-center dark:text-white text-2xl font-medium z-50">
									Account Activation Pending<br /> Contact Admin for WebUI Access
								</div>

								<div class=" mt-4 text-center text-sm dark:text-gray-200 w-full">
									Your account status is currently pending activation. To access the WebUI, please
									reach out to the administrator. Admins can manage user statuses from the Admin
									Panel.
								</div>

								<div class=" mt-6 mx-auto relative group w-fit">
									<button
										class="relative z-20 flex px-5 py-2 rounded-full bg-white border border-gray-100 dark:border-none hover:bg-gray-100 text-gray-700 transition font-medium text-sm"
										on:click={async () => {
											location.href = '/';
										}}
									>
										{$i18n.t('Check Again')}
									</button>

									<button
										class="text-xs text-center w-full mt-2 text-gray-400 underline"
										on:click={async () => {
											localStorage.removeItem('token');
											location.href = '/auth';
										}}>{$i18n.t('Sign Out')}</button
									>
								</div>
							</div>
						</div>
					</div>
				</div>
			{:else if localDBChats.length > 0}
				<div class="fixed w-full h-full flex z-50">
					<div
						class="absolute w-full h-full backdrop-blur-md bg-white/20 dark:bg-gray-900/50 flex justify-center"
					>
						<div class="m-auto pb-44 flex flex-col justify-center">
							<div class="max-w-md">
								<div class="text-center dark:text-white text-2xl font-medium z-50">
									Important Update<br /> Action Required for Chat Log Storage
								</div>

								<div class=" mt-4 text-center text-sm dark:text-gray-200 w-full">
									{$i18n.t(
										"Saving chat logs directly to your browser's storage is no longer supported. Please take a moment to download and delete your chat logs by clicking the button below. Don't worry, you can easily re-import your chat logs to the backend through"
									)}
									<span class="font-semibold dark:text-white"
										>{$i18n.t('Settings')} > {$i18n.t('Chats')} > {$i18n.t('Import Chats')}</span
									>. {$i18n.t(
										'This ensures that your valuable conversations are securely saved to your backend database. Thank you!'
									)}
								</div>

								<div class=" mt-6 mx-auto relative group w-fit">
									<button
										class="relative z-20 flex px-5 py-2 rounded-full bg-white border border-gray-100 dark:border-none hover:bg-gray-100 transition font-medium text-sm"
										on:click={async () => {
											let blob = new Blob([JSON.stringify(localDBChats)], {
												type: 'application/json'
											});
											saveAs(blob, `chat-export-${Date.now()}.json`);

											const tx = DB.transaction('chats', 'readwrite');
											await Promise.all([tx.store.clear(), tx.done]);
											await deleteDB('Chats');

											localDBChats = [];
										}}
									>
										Download & Delete
									</button>

									<button
										class="text-xs text-center w-full mt-2 text-gray-400 underline"
										on:click={async () => {
											localDBChats = [];
										}}>{$i18n.t('Close')}</button
									>
								</div>
							</div>
						</div>
					</div>
				</div>
			{/if}

			<Sidebar />
			<slot />
		{:else}
			<div class="fixed w-full h-full flex z-[999]">
				<div
					class="absolute w-full h-full flex items-center justify-center"
				>
				<div class="px-2 flex items-center space-x-2">
					<svg
						class=" w-8 h-8"
						viewBox="0 0 24 24"
						fill="currentColor"
						xmlns="http://www.w3.org/2000/svg"
					>
						<style>
							.spinner_ajPY {
								transform-origin: center;
								animation: spinner_AtaB 0.75s infinite linear;
							}
							@keyframes spinner_AtaB {
								100% {
									transform: rotate(360deg);
								}
							}
						</style>
						<path
							d="M12,1A11,11,0,1,0,23,12,11,11,0,0,0,12,1Zm0,19a8,8,0,1,1,8-8A8,8,0,0,1,12,20Z"
							opacity=".25"
						/>
						<path
							d="M10.14,1.16a11,11,0,0,0-9,8.92A1.59,1.59,0,0,0,2.46,12,1.52,1.52,0,0,0,4.11,10.7a8,8,0,0,1,6.66-6.61A1.42,1.42,0,0,0,12,2.69h0A1.57,1.57,0,0,0,10.14,1.16Z"
							class="spinner_ajPY"
						/>
					</svg>
					<span class="text-xl"> Loading... </span>
				</div>
				</div>
			</div>
		{/if}
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
