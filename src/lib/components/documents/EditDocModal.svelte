<script lang="ts">
	import { toast } from 'svelte-sonner';
	import dayjs from 'dayjs';
	import { onMount, getContext } from 'svelte';

	import { getDocs, tagDocByName, updateDocByName } from '$lib/apis/documents';
	import Modal from '../common/Modal.svelte';
	import { documents } from '$lib/stores';
	import TagInput from '../common/Tags/TagInput.svelte';
	import Tags from '../common/Tags.svelte';
	import { addTagById } from '$lib/apis/chats';

	const i18n = getContext('i18n');

	export let show = false;
	export let selectedDoc;

	let tags = [];

	let doc = {
		name: '',
		title: '',
		content: null
	};

	const submitHandler = async () => {
		const res = await updateDocByName(localStorage.token, selectedDoc.name, {
			title: doc.title,
			name: doc.name
		}).catch((error) => {
			toast.error(error);
		});

		if (res) {
			show = false;

			documents.set(await getDocs(localStorage.token));
		}
	};

	const addTagHandler = async (tagName) => {
		if (!tags.find((tag) => tag.name === tagName) && tagName !== '') {
			tags = [...tags, { name: tagName }];

			await tagDocByName(localStorage.token, doc.name, {
				name: doc.name,
				tags: tags
			});

			documents.set(await getDocs(localStorage.token));
		} else {
			console.log('tag already exists');
		}
	};

	const deleteTagHandler = async (tagName) => {
		tags = tags.filter((tag) => tag.name !== tagName);

		await tagDocByName(localStorage.token, doc.name, {
			name: doc.name,
			tags: tags
		});

		documents.set(await getDocs(localStorage.token));
	};

	onMount(() => {
		if (selectedDoc) {
			doc = JSON.parse(JSON.stringify(selectedDoc));

			tags = doc?.content?.tags ?? [];
		}
	});
</script>

<Modal size="sm" bind:show>
	<div>
		<div class=" flex justify-between dark:text-gray-300 px-5 pt-4">
			<div class=" text-lg font-medium self-center">{$i18n.t('Edit Doc')}</div>
			<button
				class="self-center"
				on:click={() => {
					show = false;
				}}
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					viewBox="0 0 20 20"
					fill="currentColor"
					class="w-5 h-5"
				>
					<path
						d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z"
					/>
				</svg>
			</button>
		</div>
		<div class="flex flex-col md:flex-row w-full px-5 py-4 md:space-x-4 dark:text-gray-200">
			<div class=" flex flex-col w-full sm:flex-row sm:justify-center sm:space-x-6">
				<form
					class="flex flex-col w-full"
					on:submit|preventDefault={() => {
						submitHandler();
					}}
				>
					<div class=" flex flex-col space-y-1.5">
						<div class="flex flex-col w-full">
							<div class=" mb-1 text-xs text-gray-500">{$i18n.t('Name Tag')}</div>

							<div class="flex flex-1">
								<div
									class="bg-gray-200 dark:bg-gray-800 font-bold px-3 py-0.5 border border-r-0 dark:border-gray-800 rounded-l-xl flex items-center"
								>
									#
								</div>
								<input
									class="w-full rounded-r-xl py-2 px-4 text-sm dark:text-gray-300 dark:bg-gray-850 disabled:text-gray-500 dark:disabled:text-gray-500 outline-none"
									type="text"
									bind:value={doc.name}
									autocomplete="off"
									required
								/>
							</div>
						</div>

						<div class="flex flex-col w-full">
							<div class=" mb-1 text-xs text-gray-500">{$i18n.t('Title')}</div>

							<div class="flex-1">
								<input
									class="w-full rounded-xl py-2 px-4 text-sm dark:text-gray-300 dark:bg-gray-850 outline-none"
									type="text"
									bind:value={doc.title}
									autocomplete="off"
									required
								/>
							</div>
						</div>

						<div class="flex flex-col w-full">
							<div class=" mb-2 text-xs text-gray-500">{$i18n.t('Tags')}</div>

							<Tags {tags} addTag={addTagHandler} deleteTag={deleteTagHandler} />
						</div>
					</div>

					<div class="flex justify-end pt-5 text-sm font-medium">
						<button
							class=" px-4 py-2 bg-emerald-400 hover:bg-emerald-500 text-black dark:bg-emerald-700 dark:hover:bg-emerald-800 dark:text-gray-100 transition rounded-lg"
							type="submit"
						>
							{$i18n.t('Save')}
						</button>
					</div>
				</form>
			</div>
		</div>
	</div>
</Modal>

<style>
	input::-webkit-outer-spin-button,
	input::-webkit-inner-spin-button {
		/* display: none; <- Crashes Chrome on hover */
		-webkit-appearance: none;
		margin: 0; /* <-- Apparently some margin are still there even though it's hidden */
	}

	.tabs::-webkit-scrollbar {
		display: none; /* for Chrome, Safari and Opera */
	}

	.tabs {
		-ms-overflow-style: none; /* IE and Edge */
		scrollbar-width: none; /* Firefox */
	}

	input[type='number'] {
		-moz-appearance: textfield; /* Firefox */
	}
</style>
