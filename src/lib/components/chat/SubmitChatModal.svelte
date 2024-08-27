<script lang="ts">
	import Modal from '../common/Modal.svelte';

	export let submitChatHandler: () => void;
	export let show: boolean;
	export let assignmentName = "";
</script>

<Modal bind:show size="sm">
	<div class="text-gray-700 dark:text-gray-100">
		<div class=" flex justify-between dark:text-gray-300 px-5 pt-4">
			<div class=" text-lg font-medium self-center">Chat Submission</div>
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
		<div class="flex flex-col px-5 pb-4 pt-2 text-sm font-normal">
			<div class="pt-2">
				Do you want to submit this chat transcript for the assignment "{assignmentName}"?
			</div>
		</div>

		<div class="flex flex-row-reverse px-5 pb-4">
			<button class="px-4 py-2 bg-emerald-700 hover:bg-emerald-800 text-gray-100 transition rounded-lg"
				on:click={submitChatHandler}>
				Submit
			</button>
		</div>
	</div>
</Modal>
