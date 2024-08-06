<script lang="ts">
	import { toast } from 'svelte-sonner';

	import { onMount, getContext, tick } from 'svelte';
    
	import { WEBUI_NAME } from '$lib/stores';
	import { deleteClassById, getClassList } from '$lib/apis/classes';
	import DeleteModal from '../DeleteModal.svelte';

	const i18n = getContext('i18n');

	let classes = [];
    let showDeleteModal = false;

    let selectedClassName = '';
    let selectedClassId = 0;
	let searchValue = '';

	const deleteHander = async () => {
		const result = await deleteClassById(localStorage.token, selectedClassId).catch((error) => {
			toast.error(error);
		});

		if (result) {
			showDeleteModal = false;
			toast.success("Successfully deleted " + selectedClassName);

			classes = await getClassList(localStorage.token).catch((error) => {
				toast.error(error);
			});
		}
	}

	onMount(async () => {
		classes = await getClassList(localStorage.token).catch((error) => {
			toast.error(error);
		});
	});
</script>

<svelte:head>
	<title>
		Classes | {$WEBUI_NAME}
	</title>
</svelte:head>

<DeleteModal bind:show={showDeleteModal}
	deleteMessage={selectedClassName}
	deleteHandler={deleteHander}
    deleteArgs
/>

<div class=" text-lg font-semibold mb-3">Classes</div>

<div class=" flex w-full space-x-2">
	<div class="flex flex-1">
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
			bind:value={searchValue}
			placeholder={"Search Classes"}
		/>
	</div>

	<div>
		<a
			class=" px-2 py-2 rounded-xl border border-gray-200 dark:border-gray-600 dark:border-0 hover:bg-gray-100 dark:bg-gray-800 dark:hover:bg-gray-700 transition font-medium text-sm flex items-center space-x-1"
			href="/workspace/classes/create"
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
</div>
<hr class=" dark:border-gray-850 my-2.5" />

<div class=" my-2 mb-5" id="class-list">
	{#each classes.filter((c) => searchValue === '' || c.name
				.toLowerCase()
				.includes(searchValue.toLowerCase())) as class_}
		<div
            class=" flex space-x-4 cursor-pointer w-full px-3 py-2 dark:hover:bg-white/5 hover:bg-black/5 rounded-xl"
        >
            <div class=" flex flex-1 space-x-4 cursor-pointer w-full">
                <a href={`/workspace/classes/edit?id=${encodeURIComponent(class_.id)}`}>
                    <div class=" flex-1 self-center pl-5">
                        <div class=" font-bold">{class_.name}</div>
                        <div class="text-xs text-gray-400 dark:text-gray-500">
                            Instructor: {class_.instructor_name}
                        </div>
						<div class="text-xs text-gray-400 dark:text-gray-500">
                            Students: 0
                        </div>
						<div class="text-xs text-gray-400 dark:text-gray-500">
                            Assigned Prompts: test, ...
                        </div>
                    </div>
                </a>
            </div>
            <div class="flex flex-row space-x-1 self-center">
                <a
                    class="self-center w-fit text-sm px-2 py-2 dark:text-gray-300 dark:hover:text-white hover:bg-black/5 dark:hover:bg-white/5 rounded-xl"
                    type="button"
                    href={`/workspace/classes/edit?id=${encodeURIComponent(class_.id)}`}
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

                <button
                    class="self-center w-fit text-sm px-2 py-2 dark:text-gray-300 dark:hover:text-white hover:bg-black/5 dark:hover:bg-white/5 rounded-xl"
                    type="button"
                    on:click={() => {
                        showDeleteModal = true;
                        selectedClassName = class_.name;
                        selectedClassId = class_.id;
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
        </div>
	{/each}
</div>

<!-- <div class=" flex justify-end w-full mb-3">
	<div class="flex space-x-1">
		<input
			id="models-import-input"
			bind:this={modelsImportInputElement}
			bind:files={importFiles}
			type="file"
			accept=".json"
			hidden
			on:change={() => {
				console.log(importFiles);

				let reader = new FileReader();
				reader.onload = async (event) => {
					let savedModels = JSON.parse(event.target.result);
					console.log(savedModels);

					for (const model of savedModels) {
						if (model?.info ?? false) {
							if ($models.find((m) => m.id === model.id)) {
								await updateModelById(localStorage.token, model.id, model.info).catch((error) => {
									return null;
								});
							} else {
								await addNewModel(localStorage.token, model.info).catch((error) => {
									return null;
								});
							}
						}
					}

					await models.set(await getModels(localStorage.token));
				};

				reader.readAsText(importFiles[0]);
			}}
		/>

		<button
			class="flex text-xs items-center space-x-1 px-3 py-1.5 rounded-xl bg-gray-50 hover:bg-gray-100 dark:bg-gray-800 dark:hover:bg-gray-700 dark:text-gray-200 transition"
			on:click={() => {
				modelsImportInputElement.click();
			}}
		>
			<div class=" self-center mr-2 font-medium">{$i18n.t('Import Models')}</div>

			<div class=" self-center">
				<svg
					xmlns="http://www.w3.org/2000/svg"
					viewBox="0 0 16 16"
					fill="currentColor"
					class="w-3.5 h-3.5"
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
			class="flex text-xs items-center space-x-1 px-3 py-1.5 rounded-xl bg-gray-50 hover:bg-gray-100 dark:bg-gray-800 dark:hover:bg-gray-700 dark:text-gray-200 transition"
			on:click={async () => {
				downloadModels($models);
			}}
		>
			<div class=" self-center mr-2 font-medium">{$i18n.t('Export Models')}</div>

			<div class=" self-center">
				<svg
					xmlns="http://www.w3.org/2000/svg"
					viewBox="0 0 16 16"
					fill="currentColor"
					class="w-3.5 h-3.5"
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

	{#if localModelfiles.length > 0}
		<div class="flex">
			<div class=" self-center text-sm font-medium mr-4">
				{localModelfiles.length} Local Modelfiles Detected
			</div>

			<div class="flex space-x-1">
				<button
					class="self-center w-fit text-sm p-1.5 border dark:border-gray-600 rounded-xl flex"
					on:click={async () => {
						downloadModels(localModelfiles);

						localStorage.removeItem('modelfiles');
						localModelfiles = JSON.parse(localStorage.getItem('modelfiles') ?? '[]');
					}}
				>
					<div class=" self-center">
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
					</div>
				</button>
			</div>
		</div>
	{/if}
</div> -->