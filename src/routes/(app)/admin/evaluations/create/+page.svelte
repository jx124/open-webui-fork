<script lang="ts">
	import { toast } from 'svelte-sonner';

	import { goto } from '$app/navigation';
	import { user, models } from '$lib/stores';
	import { onMount, getContext } from 'svelte';

	import { createNewEvaluation, type EvaluationForm } from '$lib/apis/evaluations';
	import { getModels } from '$lib/apis';
	import ModelSelector from '$lib/components/admin/ModelSelector.svelte';

	const i18n = getContext('i18n');

	let loading = false;

	let form_data: EvaluationForm = {
        id: 0,
		title: '',
		content: '',
        selected_model_id: '',
	};

	let modelItems: {
		label: string;
		value: string;
	}[] = [];

	const submitHandler = async () => {
		loading = true;
        if (form_data.selected_model_id === "") {
			toast.error('Please select a model.');
			loading = false;
			return null;
        }

        const evaluation = await createNewEvaluation(localStorage.token, form_data).catch((error) => {
            toast.error(error);
			loading = false;
            return null;
        });

        if (evaluation) {
            await goto('/admin/evaluations');
        }

		loading = false;
	};

	onMount(async () => {
		if ($user?.role !== "admin") {
			await goto("/admin");
		}
		if (sessionStorage.evaluation) {
            const evaluation = JSON.parse(sessionStorage.evaluation);
            form_data.title = evaluation.title;
            form_data.content = evaluation.content;
            form_data.selected_model_id = evaluation.selected_model_id;
            sessionStorage.removeItem('evaluation');
        }

		$models = await getModels(localStorage.token).catch((error) => {
			toast.error(error);
		});

		modelItems = $models.map((p) => {
			return {
				label: p.name,
				value: p.id
			};
		});
	});
</script>

<div class="w-full max-h-full">
	<button
		class="flex space-x-1"
		on:click={() => {
			history.back();
		}}
	>
		<div class=" self-center">
			<svg
				xmlns="http://www.w3.org/2000/svg"
				viewBox="0 0 20 20"
				fill="currentColor"
				class="w-4 h-4"
			>
				<path
					fill-rule="evenodd"
					d="M17 10a.75.75 0 01-.75.75H5.612l4.158 3.96a.75.75 0 11-1.04 1.08l-5.5-5.25a.75.75 0 010-1.08l5.5-5.25a.75.75 0 111.04 1.08L5.612 9.25H16.25A.75.75 0 0117 10z"
					clip-rule="evenodd"
				/>
			</svg>
		</div>
		<div class=" self-center font-medium text-sm">{$i18n.t('Back')}</div>
	</button>

	<form
		class="flex flex-col max-w-2xl mx-auto mt-4 mb-10"
		on:submit|preventDefault={() => {
			submitHandler();
		}}
	>
		<div class="my-2">
			<div class=" text-sm font-semibold mb-2">{$i18n.t('Title')}*</div>

			<div>
				<input
					class="px-3 py-1.5 text-sm w-full bg-transparent border dark:border-gray-600 outline-none rounded-lg"
					placeholder={'Add a short title for this evaluation'}
					bind:value={form_data.title}
					required
				/>
			</div>
		</div>

		<div class="my-2">
			<div class="flex w-full justify-between">
				<div class=" self-center text-sm font-semibold">Evaluation Prompt Content*</div>
			</div>

			<div class="mt-2">
				<div>
					<textarea
						class="px-3 py-1.5 text-sm w-full bg-transparent border dark:border-gray-600 outline-none rounded-lg"
						placeholder={'Write your evaluation prompt here.'}
						rows="6"
						bind:value={form_data.content}
						required
					/>
				</div>

				<div class="text-xs text-gray-600 dark:text-gray-500">
					ⓘ This prompt will be sent along with the entire chat conversation to perform the evaluation.
				</div>
			</div>
		</div>

		<div class="my-2">
			<div class=" text-sm font-semibold mb-1">Model for Evaluation LLM*</div>
			<ModelSelector
				items={modelItems}
				bind:value={form_data.selected_model_id}
				externalLabel={form_data.selected_model_id}
			/>
			<div class="text-xs text-gray-600 dark:text-gray-500 mt-1">
				Select the LLM model to be used.
			</div>
		</div>

		<div class="my-2 flex justify-end">
			<button
				class=" text-sm px-3 py-2 transition rounded-xl {loading
					? ' cursor-not-allowed bg-emerald-800'
					: ' bg-emerald-400 hover:bg-emerald-500 text-black dark:bg-emerald-700 dark:hover:bg-emerald-800 dark:text-gray-100'} flex"
				type="submit"
				disabled={loading}
			>
				<div class=" self-center font-medium">{$i18n.t('Save & Create')}</div>

				{#if loading}
					<div class="ml-1.5 self-center">
						<svg
							class=" w-4 h-4"
							viewBox="0 0 24 24"
							fill="currentColor"
							xmlns="http://www.w3.org/2000/svg"
							><style>
								.spinner_ajPY {
									transform-origin: center;
									animation: spinner_AtaB 0.75s infinite linear;
								}
								@keyframes spinner_AtaB {
									100% {
										transform: rotate(360deg);
									}
								}
							</style><path
								d="M12,1A11,11,0,1,0,23,12,11,11,0,0,0,12,1Zm0,19a8,8,0,1,1,8-8A8,8,0,0,1,12,20Z"
								opacity=".25"
							/><path
								d="M10.14,1.16a11,11,0,0,0-9,8.92A1.59,1.59,0,0,0,2.46,12,1.52,1.52,0,0,0,4.11,10.7a8,8,0,0,1,6.66-6.61A1.42,1.42,0,0,0,12,2.69h0A1.57,1.57,0,0,0,10.14,1.16Z"
								class="spinner_ajPY"
							/></svg
						>
					</div>
				{/if}
			</button>
		</div>
	</form>
</div>
