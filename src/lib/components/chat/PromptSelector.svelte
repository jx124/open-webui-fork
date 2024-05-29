<script lang="ts">
	import { settings, prompts } from '$lib/stores';
	import { getContext } from 'svelte';
	import Selector from './PromptSelector/Selector.svelte';

	const i18n = getContext('i18n');

	export let selectedPrompt: string;
	export let disabled = false;


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
