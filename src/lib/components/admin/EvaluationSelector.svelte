<script lang="ts">
	import { DropdownMenu } from 'bits-ui';

	import { flyAndScale } from '$lib/utils/transitions';

	import Search from '$lib/components/icons/Search.svelte';

	import { mobile } from '$lib/stores';

	export let value = 0;
	export let placeholder = "Select an evaluation"
	export let searchEnabled = true;
	export let searchPlaceholder = "Search evaluations";

	export let items: {
        label: string,
        value: number
    } = [];

	export let className = 'w-[24rem]';

    export let externalLabel = "";

    $: if (externalLabel) {
        label = externalLabel
    }

	let show = false;
    let label = "";

    $: label = items.find(item => item.value === value)?.label;

	let searchValue = '';

    $: filteredItems = searchValue
		? items.filter((item) => item.label.toLowerCase().includes(searchValue.toLowerCase()))
		: items;
</script>


<div class="flex items-center w-full">
    <DropdownMenu.Root
        bind:open={show}
        onOpenChange={async () => {
            searchValue = '';
            window.setTimeout(() => document.getElementById('evaluation-search-input')?.focus(), 0);
        }}
    >
    
        <DropdownMenu.Trigger aria-label={placeholder} class="w-full">
            <input
                class="px-3 py-1.5 text-sm w-full bg-transparent border dark:border-gray-600 outline-none rounded-lg disabled:opacity-75 "
                {placeholder}
                bind:value={label}
                required
                readonly
            />
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
                            id="evaluation-search-input"
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
                            aria-label="role-item"
                            type="button"
                            class="flex w-full text-left font-medium line-clamp-1 select-none items-center rounded-button py-2 pl-3 pr-1.5 text-sm text-gray-700 dark:text-gray-100 outline-none transition-all duration-75 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg cursor-pointer data-[highlighted]:bg-muted"
                            on:click={() => {
                                value = item.value;
                                label = item.label;
                                show = false;
                            }}
                        >
                            <div class="flex items-center gap-2">
                                <div class="">
                                    {item.label}
                                </div>
                            </div>
                        </button>
                    {:else}
                        <div class="block px-3 py-2 text-sm text-gray-700 dark:text-gray-100">
                            No results found, add more evaluations under Admin Panel > Evaluations.
                        </div>
                    {/each}
                </div>

                <div class="hidden w-[42rem]" />
                <div class="hidden w-[32rem]" />
            </slot>
        </DropdownMenu.Content>
    </DropdownMenu.Root>

    
</div>

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
