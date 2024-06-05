<script lang="ts">
	import { settings, prompts } from '$lib/stores';
	import { getContext } from 'svelte';
	import Selector from './PromptSelector/Selector.svelte';

	const i18n = getContext('i18n');

	export let selectedPromptCommand: string;
	export let disabled = false;

	$: promptTitle = $prompts.find((prompt) => prompt.command === selectedPromptCommand)?.title ?? $i18n.t('Prompt');
</script>

<div class="flex flex-col w-full items-center md:items-start">
	<div class="flex w-full max-w-fit">
		<div class="overflow-hidden w-full">
			<div class="mr-1 max-w-full">
				<Selector
					searchPlaceholder={$i18n.t('Search Prompts')}
					items={$prompts
						.map((prompt) => ({
							value: prompt.command, // command is validated to be unique
							label: prompt.title,
						}))}
					disabled={disabled}
					placeholder={promptTitle}
					bind:value={selectedPromptCommand}
				/>
			</div>
		</div>
	</div>
</div>
