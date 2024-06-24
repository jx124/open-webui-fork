<script lang="ts">
	import Modal from '../common/Modal.svelte';

	export let show: boolean;
    export let selectedPromptCommand: string;
    export let deleteHandler;
</script>

<Modal bind:show size="sm">
	<div class="text-gray-700 dark:text-gray-100">
		<div class=" flex justify-between dark:text-gray-300 px-5 pt-4">
			<div class=" text-lg font-medium self-center">Confirm Deletion</div>
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
		
		<div class="flex flex-col pb-2 px-5">
			<div class="self-center text-sm font-normal mr-auto">Are you sure you want to delete {selectedPromptCommand}?</div>
		</div>
		
		<div class="flex flex-row-reverse px-5 pb-4">
			<button class="px-4 py-2 bg-red-700 hover:bg-red-800 text-gray-100 transition rounded-lg"
				on:click={deleteHandler(selectedPromptCommand)}>
				Delete
			</button>
		</div>
	</div>
</Modal>
