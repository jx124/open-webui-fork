<script lang="ts">
	import { toast } from 'svelte-sonner';
	import fileSaver from 'file-saver';
	const { saveAs } = fileSaver;

	import { getContext, onMount } from 'svelte';
	import { WEBUI_NAME, prompts, selectedPromptCommand, user } from '$lib/stores';
	import { createNewPrompt, deletePromptByCommand, getPrompts } from '$lib/apis/prompts';
	import DeleteModal from '../DeleteModal.svelte';
	import DocumentDuplicate from '../icons/DocumentDuplicate.svelte';
	import Tooltip from '../common/Tooltip.svelte';
	import { goto } from '$app/navigation';

	const i18n = getContext('i18n');

	let importFiles = '';
	let query = '';
	let promptsImportInputElement: HTMLInputElement;

	let showDeleteModal = false;

	const deletePrompt = async (command) => {
		showDeleteModal = false;
		await deletePromptByCommand(localStorage.token, command).catch((err) => {
			toast.error(err);
		});
		$prompts = await getPrompts(localStorage.token);
	};

	const clonePromptHandler = async (command) => {
        let prompt = $prompts.find(p => p.command === command);
        if (!prompt) {
            toast.error("Cannot duplicate profile.");
            return;
        }

        sessionStorage.prompt = JSON.stringify({
            ...prompt,
            title: `${prompt.title} Copy`,
        });
        goto('/admin/profiles/create');
	};

	onMount(async () => {
		$prompts = await getPrompts(localStorage.token);
	});
</script>

<svelte:head>
	<title>
		Profiles | {$WEBUI_NAME}
	</title>
</svelte:head>

<DeleteModal
	bind:show={showDeleteModal}
	deleteMessage={$selectedPromptCommand}
	deleteHandler={deletePrompt}
	deleteArgs={$selectedPromptCommand}
/>

<div class=" text-lg font-semibold mb-3">Profiles</div>

<div class=" flex w-full space-x-2">
	<div class="flex flex-1 h-8">
		<div class=" self-center ml-1 mr-3">
			<svg
				xmlns="http://www.w3.org/2000/svg"
				viewBox="0 0 20 20"
				fill="currentColor"
				class="w-4 h-4"
			>
				<path
					fill-rule="evenodd"
					d="M9 3.5a5.5 5.5 0 100 11 5.5 5.5 0 000-11zM2 9a7 7 0 1112.452 4.391l3.328 3.329a.75.75 0 11-1.06 1.06l-3.329-3.328A7 7 0 012 9z"
					clip-rule="evenodd"
				/>
			</svg>
		</div>
		<input
			class=" w-full text-sm pr-4 py-1 rounded-r-xl outline-none bg-transparent"
			bind:value={query}
			placeholder={$i18n.t('Search Profiles')}
		/>
	</div>

	{#if $user?.role === "admin"}
		<div>
			<a
				class=" px-2 py-2 rounded-xl border border-gray-200 dark:border-gray-600 dark:border-0 hover:bg-gray-100 dark:bg-gray-800 dark:hover:bg-gray-700 transition font-medium text-sm flex items-center space-x-1"
				href="/admin/profiles/create"
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					viewBox="0 0 16 16"
					fill="currentColor"
					class="w-4 h-4"
				>
					<path
						d="M8.75 3.75a.75.75 0 0 0-1.5 0v3.5h-3.5a.75.75 0 0 0 0 1.5h3.5v3.5a.75.75 0 0 0 1.5 0v-3.5h3.5a.75.75 0 0 0 0-1.5h-3.5v-3.5Z"
					/>
				</svg>
			</a>
		</div>
	{/if}
</div>
<hr class=" dark:border-gray-850 my-2.5" />

<div class="my-2 mb-5" id="profile-list">
	{#each $prompts.filter((p) => query === '' 
        || p.title.toLowerCase().includes(query) 
        || p.command.toLowerCase().includes(query))
        .sort((a, b) => b.timestamp - a.timestamp) as prompt}
		<div
			class=" flex space-x-4 w-full px-3 py-2 dark:hover:bg-white/5 hover:bg-black/5 rounded-xl"
		>
			{#if $user?.role === 'admin'}
				<div class="flex flex-1 space-x-4 cursor-pointer w-full">
					<a
						class="flex items-center"
						href={`/admin/profiles/edit?command=${encodeURIComponent(prompt.command)}`}
					>
						<img
							src={prompt.image_url ? prompt.image_url : '/user.png'}
							alt="profile"
							class="rounded-full h-12 w-12 object-cover"
						/>
						<div class=" flex-1 self-center pl-3">
							<div class=" font-bold">{(prompt.is_visible ? '' : '[Draft] ') + prompt.title}</div>
						</div>
					</a>
				</div>
				<div class="flex flex-row space-x-1 self-center">
					<a
						class="self-center w-fit text-sm px-2 py-2 dark:text-gray-300 dark:hover:text-white hover:bg-black/5 dark:hover:bg-white/5 rounded-xl"
						type="button"
						href={`/admin/profiles/edit?command=${encodeURIComponent(prompt.command)}`}
					>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							fill="none"
							viewBox="0 0 24 24"
							stroke-width="1.5"
							stroke="currentColor"
							class="w-4 h-4"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L6.832 19.82a4.5 4.5 0 01-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 011.13-1.897L16.863 4.487zm0 0L19.5 7.125"
							/>
						</svg>
					</a>

                    <Tooltip content="Duplicate Profile">
                        <button
                            class="self-center w-fit text-sm px-2 py-2 dark:text-gray-300 dark:hover:text-white hover:bg-black/5 dark:hover:bg-white/5 rounded-xl"
                            on:click={() => clonePromptHandler(prompt.command) }
                        >
                            <DocumentDuplicate />
                        </button>
                    </Tooltip>
					<button
						class="self-center w-fit text-sm px-2 py-2 dark:text-gray-300 dark:hover:text-white hover:bg-black/5 dark:hover:bg-white/5 rounded-xl"
						type="button"
						on:click={() => {
							showDeleteModal = true;
							$selectedPromptCommand = prompt.command;
						}}
					>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							fill="none"
							viewBox="0 0 24 24"
							stroke-width="1.5"
							stroke="currentColor"
							class="w-4 h-4"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0"
							/>
						</svg>
					</button>
				</div>
			{:else}
				<div class="flex flex-1 space-x-4 w-full">
					<div
						class="flex items-center"
					>
						<img
							src={prompt.image_url ? prompt.image_url : '/user.png'}
							alt="profile"
							class="rounded-full h-12 w-12 object-cover"
						/>
						<div class=" flex-1 self-center pl-3">
							<div class=" font-bold">{(prompt.is_visible ? '' : '[Draft] ') + prompt.title}</div>
						</div>
					</div>
				</div>
			{/if}
		</div>
	{/each}
</div>

{#if $user?.role === 'admin'}
	<div class=" flex justify-end w-full mb-3">
		<div class="flex space-x-2">
			<input
				id="prompts-import-input"
				bind:this={promptsImportInputElement}
				bind:files={importFiles}
				type="file"
				accept=".json"
				hidden
				on:change={() => {
					console.log(importFiles);

					const reader = new FileReader();
					reader.onload = async (event) => {
						const savedPrompts = JSON.parse(event.target.result);
						console.log(savedPrompts);

						for (const prompt of savedPrompts) {
							await createNewPrompt(localStorage.token, prompt).catch((error) => {
								toast.error(error);
								return null;
							});
						}

						await prompts.set(await getPrompts(localStorage.token));
					};

					reader.readAsText(importFiles[0]);
				}}
			/>

			<button
				class="flex text-xs items-center space-x-1 px-3 py-1.5 rounded-xl bg-gray-200 hover:bg-gray-300 dark:hover:bg-gray-700 dark:bg-gray-800 dark:text-gray-100 text-gray-900 transition"
				on:click={() => {
					promptsImportInputElement.click();
				}}
			>
				<div class=" self-center mr-2 font-medium">{$i18n.t('Import Prompts')}</div>

				<div class=" self-center">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						viewBox="0 0 16 16"
						fill="currentColor"
						class="w-4 h-4"
					>
						<path
							fill-rule="evenodd"
							d="M4 2a1.5 1.5 0 0 0-1.5 1.5v9A1.5 1.5 0 0 0 4 14h8a1.5 1.5 0 0 0 1.5-1.5V6.621a1.5 1.5 0 0 0-.44-1.06L9.94 2.439A1.5 1.5 0 0 0 8.878 2H4Zm4 9.5a.75.75 0 0 1-.75-.75V8.06l-.72.72a.75.75 0 0 1-1.06-1.06l2-2a.75.75 0 0 1 1.06 0l2 2a.75.75 0 1 1-1.06 1.06l-.72-.72v2.69a.75.75 0 0 1-.75.75Z"
							clip-rule="evenodd"
						/>
					</svg>
				</div>
			</button>

			<button
				class="flex text-xs items-center space-x-1 px-3 py-1.5 rounded-xl bg-gray-200 hover:bg-gray-300 dark:hover:bg-gray-700 dark:bg-gray-800 dark:text-gray-100 text-gray-900 transition"
				on:click={async () => {
					// promptsImportInputElement.click();
					let blob = new Blob([JSON.stringify($prompts)], {
						type: 'application/json'
					});
					saveAs(blob, `prompts-export-${Date.now()}.json`);
				}}
			>
				<div class=" self-center mr-2 font-medium">{$i18n.t('Export Prompts')}</div>

				<div class=" self-center">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						viewBox="0 0 16 16"
						fill="currentColor"
						class="w-4 h-4"
					>
						<path
							fill-rule="evenodd"
							d="M4 2a1.5 1.5 0 0 0-1.5 1.5v9A1.5 1.5 0 0 0 4 14h8a1.5 1.5 0 0 0 1.5-1.5V6.621a1.5 1.5 0 0 0-.44-1.06L9.94 2.439A1.5 1.5 0 0 0 8.878 2H4Zm4 3.5a.75.75 0 0 1 .75.75v2.69l.72-.72a.75.75 0 1 1 1.06 1.06l-2 2a.75.75 0 0 1-1.06 0l-2-2a.75.75 0 0 1 1.06-1.06l.72.72V6.25A.75.75 0 0 1 8 5.5Z"
							clip-rule="evenodd"
						/>
					</svg>
				</div>
			</button>
		</div>
	</div>
{/if}
