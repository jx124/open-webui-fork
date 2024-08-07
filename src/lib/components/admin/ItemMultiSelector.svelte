<script lang="ts">
	import { DropdownMenu } from 'bits-ui';

	import { flyAndScale } from '$lib/utils/transitions';
	import { getContext, onMount } from 'svelte';

	import Search from '$lib/components/icons/Search.svelte';

	import { mobile } from '$lib/stores';

	const i18n = getContext('i18n');

	export let addItemLabel = "Add Item";
	export let searchEnabled = true;
	export let searchPlaceholder = "Search Items";

    type ItemType = {
		label: string,
		value: number
	};

	export let items: ItemType[] = [];
    export let selectedItems: number[] = [];

    let _selectedItems: ItemType[] = [];
    let _unselectedItems: ItemType[] = [];

	export let className = 'w-[12rem]';

	let show = false;

	let searchValue = '';

	$: filteredItems = searchValue
		? _unselectedItems.filter((item) => item.label.toLowerCase().includes(searchValue.toLowerCase()))
		: _unselectedItems;

    const getColor = (item: string) => {
        // Adapted from https://stackoverflow.com/questions/7616461/generate-a-hash-from-string-in-javascript
        let hash = 0;
        for (let i = 0; i < item.length; i++) {
            let chr = item.charCodeAt(i);
            hash = ((hash << 5) - hash) + chr;
            hash |= 0; // Convert to 32bit integer
        }
        hash = Math.max(hash, -hash);
        
        const colorList = ["red", "orange", "amber", "yellow", "lime", "green", "emerald", "teal",
            "cyan", "sky", "blue", "indigo", "violet", "purple", "fuchsia", "pink", "rose"];
        return colorList[hash % colorList.length];
    }

    const buttonColors = {
        "gray":      "text-gray-600 dark:text-gray-200 bg-gray-200/30",
        "red":       "text-red-600 dark:text-red-200 bg-red-200/30",
        "orange":    "text-orange-600 dark:text-orange-200 bg-orange-200/30",
        "amber":     "text-amber-600 dark:text-amber-200 bg-amber-200/30",
        "yellow":    "text-yellow-600 dark:text-yellow-200 bg-yellow-200/30",
        "lime":      "text-lime-600 dark:text-lime-200 bg-lime-200/30",
        "green":     "text-green-600 dark:text-green-200 bg-green-200/30",
        "emerald":   "text-emerald-600 dark:text-emerald-200 bg-emerald-200/30",
        "teal":      "text-teal-600 dark:text-teal-200 bg-teal-200/30",
        "cyan":      "text-cyan-600 dark:text-cyan-200 bg-cyan-200/30",
        "sky":       "text-sky-600 dark:text-sky-200 bg-sky-200/30",
        "blue":      "text-blue-600 dark:text-blue-200 bg-blue-200/30",
        "indigo":    "text-indigo-600 dark:text-indigo-200 bg-indigo-200/30",
        "violet":    "text-violet-600 dark:text-violet-200 bg-violet-200/30",
        "purple":    "text-purple-600 dark:text-purple-200 bg-purple-200/30",
        "fuchsia":   "text-fuchsia-600 dark:text-fuchsia-200 bg-fuchsia-200/30",
        "pink":      "text-pink-600 dark:text-pink-200 bg-pink-200/30",
        "rose":      "text-rose-600 dark:text-rose-200 bg-rose-200/30",
    }

    const divColors = {
        "gray":     "bg-gray-600 dark:bg-gray-300",
        "red":      "bg-red-600 dark:bg-red-300",
        "orange":   "bg-orange-600 dark:bg-orange-300",
        "amber":    "bg-amber-600 dark:bg-amber-300",
        "yellow":   "bg-yellow-600 dark:bg-yellow-300",
        "lime":     "bg-lime-600 dark:bg-lime-300",
        "green":    "bg-green-600 dark:bg-green-300",
        "emerald":  "bg-emerald-600 dark:bg-emerald-300",
        "teal":     "bg-teal-600 dark:bg-teal-300",
        "cyan":     "bg-cyan-600 dark:bg-cyan-300",
        "sky":      "bg-sky-600 dark:bg-sky-300",
        "blue":     "bg-blue-600 dark:bg-blue-300",
        "indigo":   "bg-indigo-600 dark:bg-indigo-300",
        "violet":   "bg-violet-600 dark:bg-violet-300",
        "purple":   "bg-purple-600 dark:bg-purple-300",
        "fuchsia":  "bg-fuchsia-600 dark:bg-fuchsia-300",
        "pink":     "bg-pink-600 dark:bg-pink-300",
        "rose":     "bg-rose-600 dark:bg-rose-300",
    }

    $: if (selectedItems) {
        _selectedItems = items.filter((item) => selectedItems.includes(item.value));
        _unselectedItems = items.filter((item) => !selectedItems.includes(item.value));
    };
</script>


<div class="flex items-center w-full">
    <DropdownMenu.Root
        bind:open={show}
        onOpenChange={async () => {
            searchValue = '';
            window.setTimeout(() => document.getElementById('item-search-input')?.focus(), 0);
        }}
    >
        <div class="flex flex-wrap min-h-10 px-3 pt-2 w-full bg-transparent border dark:border-gray-600 outline-none rounded-lg">
            {#each _selectedItems as item}
                <div
                    class="flex items-center text-nowrap w-fit gap-2 text-xs px-3 py-0.5 mr-2 mb-2 rounded-lg {`${buttonColors[getColor(item.label)]}`}"
                >
                    <div
                        class="w-1 h-1 rounded-full {`${divColors[getColor(item.label)]}`}"
                    />
                        {item.label}
                    <button
                        class="self-center"
                        type="button"
                        on:click={() => {
                            selectedItems = selectedItems.filter(
                                (selected) => selected !== item.value
                            );
                        }}
                    >
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 20 20"
                            fill="currentColor"
                            class="w-3 h-3"
                        >
                            <path
                                d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z"
                            />
                        </svg>
                    </button>
                </div>
            {/each}
        </div>

        <DropdownMenu.Trigger aria-label={addItemLabel}>
            <button class="text-sm px-3 py-2 ml-2 transition rounded-xl bg-gray-50 hover:bg-gray-100 dark:bg-gray-700 dark:hover:bg-gray-800"
                type="button"
            >
                <div class="self-center text-sm font-medium text-nowrap">{addItemLabel}</div>
            </button>
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
                            id="item-search-input"
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
                            aria-label="item-item"
                            type="button"
                            class="flex w-full text-left font-medium line-clamp-1 select-none items-center rounded-button py-2 pl-3 pr-1.5 text-sm text-gray-700 dark:text-gray-100 outline-none transition-all duration-75 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg cursor-pointer data-[highlighted]:bg-muted"
                            on:click={() => {
                                selectedItems = [ ...selectedItems, item.value ]
                            }}
                        >
                            <div class="flex items-center gap-2">
                                <div class="">
                                    {item.label}

                                    <span class=" text-xs font-medium text-gray-600 dark:text-gray-400"
                                        >{item.info?.details?.parameter_size ?? ''}</span
                                    >
                                </div>
                            </div>
                        </button>
                    {:else}
                        <div class="block px-3 py-2 text-sm text-gray-700 dark:text-gray-100">
                            No results found, add more classes under Workspace > Classes. 
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
