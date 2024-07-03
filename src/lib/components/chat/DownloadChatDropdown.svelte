<script lang="ts">
	import { getContext } from 'svelte';
    
    import { flyAndScale } from '$lib/utils/transitions';
    
	import { DropdownMenu } from 'bits-ui';
	import { downloadJSONExport, downloadPdf, downloadTxt } from '$lib/utils';

	const i18n = getContext('i18n');

    export let chat = null;
</script>

<DropdownMenu.Root>
    <DropdownMenu.Trigger
        class="flex gap-2 items-center px-3 py-2 text-sm  cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-850 rounded-xl"
    >
        <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="1.5"
            stroke="currentColor"
            class="size-4"
        >
            <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3"
            />
        </svg>

        <div class="flex items-center">{$i18n.t('Download')}</div>
    </DropdownMenu.Trigger>
    <DropdownMenu.Content
        class="w-full max-w-[200px] rounded-xl px-1 py-1.5 border border-gray-300/30 dark:border-gray-700/50 z-50 bg-white dark:bg-gray-850 dark:text-white shadow-lg"
        sideOffset={8}
        side="bottom"
        align="end"
        transition={flyAndScale}
    >
        <DropdownMenu.Item
            class="flex gap-2 items-center px-3 py-2 text-sm  cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 rounded-md"
            on:click={() => {
                downloadJSONExport(chat);
            }}
        >
            <div class="flex items-center line-clamp-1">{$i18n.t('Export chat (.json)')}</div>
        </DropdownMenu.Item>
        <DropdownMenu.Item
            class="flex gap-2 items-center px-3 py-2 text-sm  cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 rounded-md"
            on:click={() => {
                downloadTxt(chat);
            }}
        >
            <div class="flex items-center line-clamp-1">{$i18n.t('Plain text (.txt)')}</div>
        </DropdownMenu.Item>

        <DropdownMenu.Item
            class="flex gap-2 items-center px-3 py-2 text-sm  cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 rounded-md"
            on:click={() => {
                downloadPdf(chat);
            }}
        >
            <div class="flex items-center line-clamp-1">{$i18n.t('PDF document (.pdf)')}</div>
        </DropdownMenu.Item>
    </DropdownMenu.Content>
</DropdownMenu.Root>