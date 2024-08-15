<script lang="ts">
	import { DropdownMenu } from 'bits-ui';

	import { flyAndScale } from '$lib/utils/transitions';
	import { getContext } from 'svelte';

	import ChevronDown from '$lib/components/icons/ChevronDown.svelte';
	import Check from '$lib/components/icons/Check.svelte';
	import Search from '$lib/components/icons/Search.svelte';

	import { mobile } from '$lib/stores';

	const i18n = getContext('i18n');

	export let value = '';
	export let placeholder = $i18n.t('Prompt');
	export let searchEnabled = true;
	export let searchPlaceholder = $i18n.t('Search Prompts');

	export let items;

	export let className = 'w-[30rem]';
	export let disabled = false;

	let show = false;

	let searchValue = '';

	$: filteredItems = searchValue
		? items.filter((item) => item.value.toLowerCase().includes(searchValue.toLowerCase()))
		: items;

</script>

{#if disabled}
	<div
	class="flex w-full text-left px-0.5 outline-none bg-transparent truncate text-lg font-semibold placeholder-gray-400 focus:outline-none"
	>
		{placeholder}
	</div>
{:else}
	<DropdownMenu.Root
		bind:open={show}
		onOpenChange={async () => {
			searchValue = '';
			window.setTimeout(() => document.getElementById('prompt-search-input')?.focus(), 0);
		}}
	>
		<DropdownMenu.Trigger class="relative w-full" aria-label={placeholder}>
			<div
				class="flex w-full text-left px-0.5 outline-none bg-transparent truncate text-lg font-semibold placeholder-gray-400 focus:outline-none"
			>
				{placeholder}
				<ChevronDown className=" self-center ml-2 size-3" strokeWidth="2.5" />
			</div>
		</DropdownMenu.Trigger>

		<DropdownMenu.Content
			class=" z-40 {$mobile
				? `w-full`
				: `${className}`} max-w-[calc(100vw-1rem)] justify-start rounded-xl  bg-white dark:bg-gray-850 dark:text-white shadow-lg border border-gray-300/30 dark:border-gray-700/50  outline-none "
			transition={flyAndScale}
			side={$mobile ? 'bottom' : 'bottom-start'}
			sideOffset={4}
		>
			<slot>
				{#if searchEnabled}
					<div class="flex items-center gap-2.5 px-5 mt-3.5 mb-3">
						<Search className="size-4" strokeWidth="2.5" />

						<input
							id="prompt-search-input"
							bind:value={searchValue}
							class="w-full text-sm bg-transparent outline-none"
							placeholder={searchPlaceholder}
							autocomplete="off"
						/>
					</div>

					<hr class="border-gray-100 dark:border-gray-800" />
				{/if}

				<div class="px-3 my-2 max-h-64 overflow-y-auto scrollbar-hidden">
					{#each filteredItems as item}
						<button
							aria-label="prompt-item"
							class="flex w-full text-left font-medium line-clamp-1 select-none items-center rounded-button py-2 pl-3 pr-1.5 text-sm text-gray-700 dark:text-gray-100 outline-none transition-all duration-75 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg cursor-pointer data-[highlighted]:bg-muted"
							on:click={() => {
								value = item.value;

								show = false;
							}}
						>
							<div class="flex items-center gap-2">
								<div class="line-clamp-1">
									{item.label}

									<span class=" text-xs font-medium text-gray-600 dark:text-gray-400"
										>{item.info?.details?.parameter_size ?? ''}</span
									>
								</div>
							</div>

							{#if value === item.value}
								<div class="ml-auto">
									<Check />
								</div>
							{/if}
						</button>
					{:else}
						{#if items.length != 0}
							<div>
								<div class="block px-3 py-2 text-sm text-gray-700 dark:text-gray-100">
									{$i18n.t('No results found')}
								</div>
							</div>
						{:else}
							<div>
								<div class="block px-3 py-2 text-sm text-gray-700 dark:text-gray-100">
									No results found, add profiles under "Workspace" > "Profiles"
								</div>
							</div>
						{/if}
					{/each}
				</div>

				<div class="hidden w-[42rem]" />
				<div class="hidden w-[32rem]" />
			</slot>
		</DropdownMenu.Content>
	</DropdownMenu.Root>
{/if}

<style>
	.scrollbar-hidden:active::-webkit-scrollbar-thumb,
	.scrollbar-hidden:focus::-webkit-scrollbar-thumb,
	.scrollbar-hidden:hover::-webkit-scrollbar-thumb {
		visibility: visible;
	}
	.scrollbar-hidden::-webkit-scrollbar-thumb {
		visibility: hidden;
	}
</style>
