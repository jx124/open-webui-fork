<script lang="ts">
	import { DropdownMenu } from 'bits-ui';

	import { flyAndScale } from '$lib/utils/transitions';

	import { mobile } from '$lib/stores';
	import ChevronDown from '../icons/ChevronDown.svelte';

	export let value = 0;
	export let placeholder = "Select a class"

	export let items: {
		label: string;
		value: number;
	}[] = [];

	export let className = 'w-[14rem]';

	let show = false;
    let label;

    $: if (items) {
        value = items.at(0)?.value ?? 0;
    }

    $: label = items.find(item => item.value === value)?.label;
</script>


<div class="flex items-center w-full">
    <DropdownMenu.Root
        bind:open={show}
    >
    
        <DropdownMenu.Trigger aria-label={placeholder} class="w-full">
            <div class="flex pl-3 pr-2 items-center text-sm dark:text-white w-full bg-transparent border dark:border-gray-600 outline-none rounded-lg">
                <input
                    class="py-1.5 bg-transparent pointer-events-none disabled:opacity-75 "
                    {placeholder}
                    bind:value={label}
                    required
                    readonly
                />
                <ChevronDown />
            </div>
        </DropdownMenu.Trigger>

        <DropdownMenu.Content
            class=" z-40 {$mobile
                ? `w-full`
                : `${className}`} max-w-[calc(100vw-1rem)] justify-start rounded-xl bg-white dark:bg-gray-850 dark:text-white shadow-lg border border-gray-300/30 dark:border-gray-700/50  outline-none "
            transition={flyAndScale}
            side={$mobile ? 'bottom' : 'bottom-start'}
            sideOffset={4}
        >
            <slot>
                <div class="px-3 my-2 max-h-64 overflow-y-auto scrollbar-hidden">
                    {#each items as item}
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

