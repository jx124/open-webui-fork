<script lang="ts">
	import { settings, prompts } from '$lib/stores';
	import { getContext } from 'svelte';
	import Selector from './PromptSelector/Selector.svelte';

	const i18n = getContext('i18n');

	export let selectedPromptCommand: string;
	export let disabled = false;

	$: promptTitle = $prompts.find((prompt) => prompt.command === selectedPromptCommand)?.title ?? $i18n.t('Prompt');
</script>

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
