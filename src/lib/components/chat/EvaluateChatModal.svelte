<script lang="ts">
	import Modal from '../common/Modal.svelte';

	export let evaluateChatHandler: () => void;
	export let show: boolean;
	
	const selectedEvalMethod: string = "Motivational Interviewing";
	const selectedEvalSkills: string[] = [
		"Affirmation",
		"Emphasizing Autonomy",
		"Open Questions",
		"Closed Questions",
		"Persuasion (with Permission)",
		"Reflection",
		"Seeking Collaboration"
	];
</script>

<Modal bind:show size="sm">
	<div class="text-gray-700 dark:text-gray-100">
		<div class=" flex justify-between dark:text-gray-300 px-5 pt-4">
			<div class=" text-lg font-medium self-center">End Chat</div>
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
			<div>
				You cannot continue the conversation after ending the chat. You may choose to <span class="underline">submit</span> 
				the conversation or <span class="underline">restart</span> the conversation if the assignment permits.
			</div>

			<div class="pt-2">
				Do you want to proceed?
			</div>
		</div>

		<div class="flex flex-row-reverse px-5 pb-4">
			<button class="px-4 py-2 bg-emerald-700 hover:bg-emerald-800 text-gray-100 transition rounded-lg"
				on:click={evaluateChatHandler}>
				End Chat
			</button>
		</div>
	</div>
</Modal>
