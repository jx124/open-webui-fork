<script lang="ts">
	import { WEBUI_BASE_URL } from '$lib/constants';
	import { config, user, models as _models } from '$lib/stores';
	import { onMount, getContext } from 'svelte';

	import { blur, fade } from 'svelte/transition';

	import Suggestions from '../MessageInput/Suggestions.svelte';

	const i18n = getContext('i18n');

	export let modelIds = [];
	export let models = [];

	export let submitPrompt;

	let mounted = false;
	let selectedModelIdx = 0;

	$: if (modelIds.length > 0) {
		selectedModelIdx = models.length - 1;
	}

	$: models = modelIds.map((id) => $_models.find((m) => m.id === id));

	onMount(() => {
		mounted = true;
	});
</script>

{#key mounted}
	<div class="m-auto w-full max-w-6xl px-8 lg:px-24 pb-16">
		<div class="flex justify-start">
			<div class="flex -space-x-4 mb-1" in:fade={{ duration: 200 }}>
				{#each models as model, modelIdx}
					<button
						on:click={() => {
							selectedModelIdx = modelIdx;
						}}
					>
						<img
							crossorigin="anonymous"
							src={model?.info?.meta?.profile_image_url ??
								($i18n.language === 'dg-DG' ? `/doge.png` : `${WEBUI_BASE_URL}/static/favicon.png`)}
							class=" size-[2.7rem] rounded-full border-[1px] border-gray-200 dark:border-none"
							alt="logo"
							draggable="false"
						/>
					</button>
				{/each}
			</div>
		</div>

		<div
			class=" mt-2 mb-4 text-3xl text-gray-800 dark:text-gray-100 font-semibold text-left flex items-center gap-4"
		>
			<div>
				<div class=" capitalize line-clamp-1" in:fade={{ duration: 200 }}>
					{$i18n.t('Hello, {{name}}', { name: $user.name })}
				</div>

				<div class="flex flex-col" in:fade={{ duration: 200, delay: 200 }}>
					<div class="text-xl font-normal text-gray-600 dark:text-gray-500 pb-2">
						Select a model and service user profile under "Prompt" to begin chatting with the simulated 
						service user through text.
					</div>

					<div class="text-xl font-normal text-gray-600 dark:text-gray-500 pb-2">
						Our tool, based on Egan's Skilled Helper Model, is designed to help you practice your skills 
						through role-playing with a simulated client. Egan's model comprises three stages: understanding 
						the current situation (Stage 1), envisioning a better future (Stage 2), and developing an action 
						plan (Stage 3).
					</div>

					<div class="text-xl font-bold text-gray-600 dark:text-gray-500">
						This tool focuses on Stage 1, where the goal is to understand the client's current situation 
						through active listening and exploration. The central question here is, "What's going on?"
					</div>
				</div>
			</div>
		</div>

		<div class=" w-full" in:fade={{ duration: 200, delay: 300 }}>
			<Suggestions
				suggestionPrompts={models[selectedModelIdx]?.info?.meta?.suggestion_prompts ??
					$config.default_prompt_suggestions}
				{submitPrompt}
			/>
		</div>
	</div>
{/key}
