<script lang="ts">
	import { DropdownMenu } from 'bits-ui';

	import { flyAndScale } from '$lib/utils/transitions';
	import { getContext, onMount } from 'svelte';

	import Search from '$lib/components/icons/Search.svelte';

	import { mobile, prompts } from '$lib/stores';
	import XMark from '../icons/XMark.svelte';

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
        
        <div class="flex flex-col items-start w-full">
            <div class="mb-3 w-full">
                {#each $prompts.filter((p) => selectedItems.includes(p.id)) as prompt}
                    <div
                        class=" flex space-x-4 w-full px-3 py-2 dark:hover:bg-white/5 hover:bg-black/5 rounded-xl"
                    >
                        <div class="flex flex-1 space-x-4 w-full">
                            <div class="flex items-center ">
                                <img
                                    src={prompt.image_url ? prompt.image_url : "/user.png"}
                                    alt="profile"
                                    class="rounded-full h-12 w-12 object-cover"
                                />
                                <div class=" flex-1 self-center pl-3">
                                    <div class=" font-bold">{(prompt.is_visible ? "" : "[Draft] ") + prompt.title}</div>
                                    <div class=" text-xs overflow-hidden text-ellipsis line-clamp-1">
                                        {prompt.command}
                                    </div>
                                    {#if prompt.deadline}
                                        <div class="text-xs text-gray-400 dark:text-gray-500">
                                            Due: {new Date(prompt.deadline).toString()}
                                        </div>
                                    {/if}
                                </div>
                            </div>
                        </div>
                        <div class="flex flex-row space-x-1 self-center">
                            <button
                                class="self-center w-fit text-sm px-2 py-2 dark:text-gray-300 dark:hover:text-white hover:bg-black/5 dark:hover:bg-white/5 rounded-xl"
                                type="button"
                                on:click={() => {
                                    selectedItems = selectedItems.filter(
                                        (selected) => selected !== prompt.id
                                    );
                                }}
                            >
                                <XMark />
                            </button>
                        </div>
                    </div>
                {/each}
            </div>
            <DropdownMenu.Trigger aria-label={addItemLabel}>
                <button class="text-sm px-3 py-2 transition rounded-xl bg-gray-50 hover:bg-gray-100 dark:bg-gray-700 dark:hover:bg-gray-800"
                    type="button"
                >
                    <div class="self-center text-sm font-medium text-nowrap">{addItemLabel}</div>
                </button>
            </DropdownMenu.Trigger>
        </div>

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
