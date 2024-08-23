<script lang="ts">
	import { prompts, selectedPromptCommand } from '$lib/stores';
	import { getContext } from 'svelte';
	import Selector from './PromptSelector/Selector.svelte';

	const i18n = getContext('i18n');

	export let disabled = false;

	$: promptTitle = $prompts.find((prompt) => prompt.command === $selectedPromptCommand)?.title ?? 'Profile';
</script>

<Selector
	searchPlaceholder={$i18n.t('Search Profiles')}
	items={$prompts
		.map((prompt) => ({
			value: prompt.command, // command is validated to be unique
			label: prompt.title,
		}))}
	disabled={disabled}
	placeholder={promptTitle}
/>
