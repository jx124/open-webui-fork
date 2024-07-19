<script lang="ts">
	import { DropdownMenu } from 'bits-ui';

	import { flyAndScale } from '$lib/utils/transitions';
	import { getContext } from 'svelte';

	import Check from '$lib/components/icons/Check.svelte';
	import Search from '$lib/components/icons/Search.svelte';

	import { mobile } from '$lib/stores';

	const i18n = getContext('i18n');

	export let value = '';
	export let placeholder = $i18n.t('Role');
	export let searchEnabled = true;
	export let searchPlaceholder = "Search Roles";

	export let items;

	export let className = 'w-[12rem]';

    export let user;
    export let updateRoleHandler: Function;

	let show = false;

	let searchValue = '';

	$: filteredItems = searchValue
		? items.filter((item) => item.value.toLowerCase().includes(searchValue.toLowerCase()))
		: items;

    const getRoleColor = (role: string) => {
        if (role === "admin") {
            return "sky";
        }
        if (role === "pending") {
            return "gray";
        }
        if (role === "user") {
            return "green";
        }

        // Adapted from https://stackoverflow.com/questions/7616461/generate-a-hash-from-string-in-javascript
        let hash = 0;
        for (let i = 0; i < role.length; i++) {
            let chr = role.charCodeAt(i);
            hash = ((hash << 5) - hash) + chr;
            hash |= 0; // Convert to 32bit integer
        }
        hash = Math.max(hash, -hash);
        
        const colorList = ["red", "orange", "amber", "yellow", "lime", "green", "emerald", "teal",
            "cyan", "sky", "blue", "indigo", "violet", "purple", "fuchsia", "pink", "rose"];
        return colorList[hash % colorList.length];
    }

    $: roleColor = getRoleColor(value);
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
</script>


<DropdownMenu.Root
    bind:open={show}
    onOpenChange={async () => {
        searchValue = '';
        window.setTimeout(() => document.getElementById('role-search-input')?.focus(), 0);
    }}
>
    
    <DropdownMenu.Trigger class="relative w-full" aria-label={placeholder}>
        <button
            class=" flex items-center gap-2 text-xs px-3 py-0.5 rounded-lg {`${buttonColors[roleColor]}`}"
        >
        <div
            class="w-1 h-1 rounded-full {`${divColors[roleColor]}`}"
        />
            {$i18n.t(user.role)}
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
                        class="flex w-full text-left font-medium line-clamp-1 select-none items-center rounded-button py-2 pl-3 pr-1.5 text-sm text-gray-700 dark:text-gray-100 outline-none transition-all duration-75 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg cursor-pointer data-[highlighted]:bg-muted"
                        on:click={() => {
                            value = item.value;
                            updateRoleHandler(user.id, value);
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

                        {#if value === item.value}
                            <div class="ml-auto">
                                <Check />
                            </div>
                        {/if}
                    </button>
                {:else}
                    <div class="block px-3 py-2 text-sm text-gray-700 dark:text-gray-100">
                        No results found, add more roles under 
                        <span class="inline-flex">
                            Admin Settings
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                viewBox="0 0 16 16"
                                fill="currentColor"
                                class="ml-1 w-4 h-4 items-baseline"
                            >
                                <path
                                    fill-rule="evenodd"
                                    d="M6.955 1.45A.5.5 0 0 1 7.452 1h1.096a.5.5 0 0 1 .497.45l.17 1.699c.484.12.94.312 1.356.562l1.321-1.081a.5.5 0 0 1 .67.033l.774.775a.5.5 0 0 1 .034.67l-1.08 1.32c.25.417.44.873.561 1.357l1.699.17a.5.5 0 0 1 .45.497v1.096a.5.5 0 0 1-.45.497l-1.699.17c-.12.484-.312.94-.562 1.356l1.082 1.322a.5.5 0 0 1-.034.67l-.774.774a.5.5 0 0 1-.67.033l-1.322-1.08c-.416.25-.872.44-1.356.561l-.17 1.699a.5.5 0 0 1-.497.45H7.452a.5.5 0 0 1-.497-.45l-.17-1.699a4.973 4.973 0 0 1-1.356-.562L4.108 13.37a.5.5 0 0 1-.67-.033l-.774-.775a.5.5 0 0 1-.034-.67l1.08-1.32a4.971 4.971 0 0 1-.561-1.357l-1.699-.17A.5.5 0 0 1 1 8.548V7.452a.5.5 0 0 1 .45-.497l1.699-.17c.12-.484.312-.94.562-1.356L2.629 4.107a.5.5 0 0 1 .034-.67l.774-.774a.5.5 0 0 1 .67-.033L5.43 3.71a4.97 4.97 0 0 1 1.356-.561l.17-1.699ZM6 8c0 .538.212 1.026.558 1.385l.057.057a2 2 0 0 0 2.828-2.828l-.058-.056A2 2 0 0 0 6 8Z"
                                    clip-rule="evenodd"
                                />
                            </svg>
                        </span>
                        > Users.
                    </div>
                {/each}
            </div>

            <div class="hidden w-[42rem]" />
            <div class="hidden w-[32rem]" />
        </slot>
    </DropdownMenu.Content>
</DropdownMenu.Root>

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
