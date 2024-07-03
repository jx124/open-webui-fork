<script lang="ts">
	import Modal from "../common/Modal.svelte";
	import sanitizeHtml from 'sanitize-html';

    export let show = false;
    export let previewContent;
</script>

<Modal bind:show size='sm'>
    <div class="text-gray-700 dark:text-gray-100">
		<div class=" flex justify-between dark:text-gray-300 px-5 pt-4">
			<div class=" text-lg font-medium self-center">Additional Information HTML Preview</div>
			<button
				class="self-center"
				on:click={() => {
					show = false;
				}}
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					viewBox="0 0 20 20"
					fill="currentColor"
					class="w-5 h-5"
				>
					<path
						d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z"
					/>
				</svg>
			</button>
		</div>
		
		<div class="flex flex-col pb-2 px-5 mt-2 mb-6 min-h-48 max-h-96">
			<div class="prose flex flex-col text-sm whitespace-pre-line font-normal mr-auto w-full h-full overflow-auto overscroll-contain
                dark:prose-invert prose-headings:my-0 prose-p:my-0 prose-p:mb-0 prose-pre:my-0 prose-table:my-0 prose-blockquote:my-0 prose-img:my-0 prose-ul:-my-1 prose-ol:-my-1 prose-li:-my-1 prose-ul:-mb-3 prose-ol:-mb-3 prose-li:-mb-1">
                {#if previewContent}
                    {@html sanitizeHtml(previewContent)}
                {:else}
                    No additional information provided.
                {/if}
            </div>
		</div>
	</div>
</Modal>