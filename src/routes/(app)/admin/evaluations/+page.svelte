<script lang="ts">
	import { goto } from '$app/navigation';
	import { deleteEvaluationById, type EvaluationForm, getEvaluations } from '$lib/apis/evaluations';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import DeleteModal from '$lib/components/DeleteModal.svelte';
	import DocumentDuplicate from '$lib/components/icons/DocumentDuplicate.svelte';
	import { evaluations, WEBUI_NAME } from '$lib/stores';
	import { onMount } from 'svelte';
	import { toast } from 'svelte-sonner';

	let searchValue = '';
	let showDeleteModal = false;
	let selectedEval: EvaluationForm;

	const deleteEvalHandler = async (id: number) => {
		await deleteEvaluationById(localStorage.token, id).catch((err) => toast.error(err));
		showDeleteModal = false;
		$evaluations = await getEvaluations(localStorage.token);
	}

	const cloneEvalHandler = async (evaluation) => {
        if (!evaluation) {
            toast.error("Cannot duplicate evaluation.");
            return;
        }

        sessionStorage.evaluation = JSON.stringify({
            ...evaluation,
            title: `${evaluation.title} Copy`,
        });
        goto('/admin/evaluations/create');
	};

	onMount(async () => {
		$evaluations = await getEvaluations(localStorage.token);
	});
</script>

<svelte:head>
	<title>
		Evaluations | {$WEBUI_NAME}
	</title>
</svelte:head>

<DeleteModal
	bind:show={showDeleteModal}
	deleteMessage={selectedEval?.title}
	deleteHandler={deleteEvalHandler}
	deleteArgs={selectedEval?.id}
/>

<div class=" text-lg font-semibold mb-3">Evaluations</div>

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
			placeholder={'Search Evaluations'}
		/>
	</div>

	<div>
		<a
			class=" px-2 py-2 rounded-xl border border-gray-200 dark:border-gray-600 dark:border-0 hover:bg-gray-100 dark:bg-gray-800 dark:hover:bg-gray-700 transition font-medium text-sm flex items-center space-x-1"
			href="/admin/evaluations/create"
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

<div class="my-2 mb-5" id="profile-list">
	{#each $evaluations.filter((evaluation) => searchValue === '' 
		|| evaluation.title.toLowerCase().includes(searchValue) 
		|| evaluation.content.toLowerCase().includes(searchValue)) as evaluation}
		<div class=" flex space-x-4 w-full px-3 py-2 dark:hover:bg-white/5 hover:bg-black/5 rounded-xl">
			<div class="flex flex-1 space-x-4 cursor-pointer w-full">
				<a
					class="flex items-center"
					href={`/admin/evaluations/edit?id=${evaluation.id}`}
				>
					<div class=" flex-1 self-center pl-3">
						<div class="font-bold">{evaluation.title}</div>
						<p class="text-xs line-clamp-1 text-ellipsis overflow-hidden max-w-[40rem]">{evaluation.content}</p>
					</div>
				</a>
			</div>
			<div class="flex flex-row space-x-1 self-center">
				<a
					class="self-center w-fit text-sm px-2 py-2 dark:text-gray-300 dark:hover:text-white hover:bg-black/5 dark:hover:bg-white/5 rounded-xl"
					type="button"
					href={`/admin/evaluations/edit?id=${evaluation.id}`}
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

                <Tooltip content="Duplicate Evaluation">
                    <button
                        class="self-center w-fit text-sm px-2 py-2 dark:text-gray-300 dark:hover:text-white hover:bg-black/5 dark:hover:bg-white/5 rounded-xl"
                        on:click={() => cloneEvalHandler(evaluation) }
                    >
                        <DocumentDuplicate />
                    </button>
                </Tooltip>
				<button
					class="self-center w-fit text-sm px-2 py-2 dark:text-gray-300 dark:hover:text-white hover:bg-black/5 dark:hover:bg-white/5 rounded-xl"
					type="button"
					on:click={() => {
						showDeleteModal = true;
						selectedEval = evaluation;
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
