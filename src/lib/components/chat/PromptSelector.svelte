<script lang="ts">
	import { setDefaultModels } from '$lib/apis/configs';
	import { models, showSettings, settings, user, mobile, prompts } from '$lib/stores';
	import { onMount, tick, getContext } from 'svelte';
	import { toast } from 'svelte-sonner';
	import Selector from './PromptSelector/Selector.svelte';
	import Tooltip from '../common/Tooltip.svelte';

	const i18n = getContext('i18n');

	export let selectedPrompt;
	export let disabled = false;

	export let showSetDefault = true;

	// const saveDefaultModel = async () => {
	// 	const hasEmptyModel = selectedModels.filter((it) => it === '');
	// 	if (hasEmptyModel.length) {
	// 		toast.error($i18n.t('Choose a model before saving...'));
	// 		return;
	// 	}
	// 	settings.set({ ...$settings, models: selectedModels });
	// 	localStorage.setItem('settings', JSON.stringify($settings));

	// 	if ($user.role === 'admin') {
	// 		console.log('setting default models globally');
	// 		await setDefaultModels(localStorage.token, selectedModels.join(','));
	// 	}
	// 	toast.success($i18n.t('Default model updated'));
	// };

</script>

<div class="flex flex-col w-full items-center md:items-start">
	<div class="flex w-full max-w-fit">
		<div class="overflow-hidden w-full">
			<div class="mr-1 max-w-full">
				<Selector
					searchPlaceholder={$i18n.t('Search Prompts')}
					items={$prompts
						.map((prompt) => ({
							value: prompt.content,
							label: prompt.title,
						}))}
					disabled={disabled}
					bind:value={selectedPrompt}
				/>
			</div>
		</div>
	</div>
</div>

{#if showSetDefault && !$mobile}
	<div class="text-left mt-0.5 ml-1 text-[0.7rem] text-gray-500">
		<!-- <button on:click={saveDefaultModel}> {$i18n.t('Set as default')}</button> -->
		<button on:click={() => alert("Not implemented")}> {$i18n.t('Set as default')}</button>
	</div>
{/if}
