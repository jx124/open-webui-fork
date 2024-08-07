<script lang="ts">
	import { DropdownMenu } from 'bits-ui';

	import { flyAndScale } from '$lib/utils/transitions';
	import { getContext, onMount } from 'svelte';

	import Search from '$lib/components/icons/Search.svelte';

	import { mobile, user } from '$lib/stores';

	const i18n = getContext('i18n');

	export let value = '';
	export let placeholder = "Select a user"
	export let searchEnabled = true;
	export let searchPlaceholder = "Search users";

	export let items = [
		{ value: 'mango', label: 'Mango' },
		{ value: 'watermelon', label: 'Watermelon' },
		{ value: 'apple', label: 'Apple' },
		{ value: 'pineapple', label: 'Pineapple' },
		{ value: 'orange', label: 'Orange' }
	];

	export let className = 'w-[24rem]';

    export let externalLabel = "";

    $: if (externalLabel) {
        label = externalLabel
    }

	let show = false;
    let label = "";

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
            window.setTimeout(() => document.getElementById('role-search-input')?.focus(), 0);
        }}
    >
    
        <DropdownMenu.Trigger aria-label={placeholder} class="w-full">
            <input
                class="px-3 py-1.5 text-sm w-full bg-transparent border dark:border-gray-600 outline-none rounded-lg"
                {placeholder}
                bind:value={label}
                required
                readonly
                disabled={$user?.role === "instructor"}
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
                            id="role-search-input"
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

                                    <span class=" text-xs font-medium text-gray-600 dark:text-gray-400"
                                        >{item.info?.details?.parameter_size ?? ''}</span
                                    >
                                </div>
                            </div>
                        </button>
                    {:else}
                        <div class="block px-3 py-2 text-sm text-gray-700 dark:text-gray-100">
                            No results found, add more users under Admin Panel > 
                            <span class="inline-flex">
                                Add Users
                                <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    viewBox="0 0 16 16"
                                    fill="currentColor"
                                    class="ml-1 w-4 h-4 items-baseline"
                                >
                                <path
                                    d="M8.75 3.75a.75.75 0 0 0-1.5 0v3.5h-3.5a.75.75 0 0 0 0 1.5h3.5v3.5a.75.75 0 0 0 1.5 0v-3.5h3.5a.75.75 0 0 0 0-1.5h-3.5v-3.5Z"
                                />
                                </svg>
                            </span>.
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
