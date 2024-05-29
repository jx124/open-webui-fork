<script lang="ts">
	import { settings, prompts } from '$lib/stores';
	import { getContext } from 'svelte';
	import Modal from '../common/Modal.svelte';

	const i18n = getContext('i18n');

	export let evaluateChatHandler: Function;

	export let selectedEvalMethod: string;
	export let selectedEvalSkills: string[] = [];
	export let show: boolean;

	let evaluationMethods = ["Motivational Interviewing"];
	let evaluationSkillsMap = new Map<string, string[]>([
		["Motivational Interviewing", [
			"Affirmation",
			"Emphasizing Autonomy",
			"Open Questions",
			"Closed Questions",
			"Persuasion (with Permission)",
			"Reflection",
			"Seeking Collaboration"
		]],
	])
	
	$: skills = evaluationSkillsMap.get(selectedEvalMethod) ?? [];
	$: selectedEvalSkills = show ? selectedEvalSkills : []; // reset everytime modal is closed

	function toggleAll(event) {
		selectedEvalSkills = event.target.checked ? [...skills] : [];
	}
</script>

<Modal bind:show size="sm">
	<div class="text-gray-700 dark:text-gray-100">
		<div class=" flex justify-between dark:text-gray-300 px-5 pt-4">
			<div class=" text-lg font-medium self-center">Evaluation</div>
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
		<div class="flex flex-col pb-4">
			<div class="flex flex-row justify-items px-5">
				<div class="self-center text-xs font-medium mr-auto">Evaluation method</div>
				<select
					class=" dark:bg-gray-900 w-fit pr-8 rounded py-2 px-2 text-xs bg-transparent outline-none text-right"
					bind:value={selectedEvalMethod}
					placeholder="Select an evaluation method"
				>
				{#each evaluationMethods as method}
					<option>{method}</option>
				{/each}
			</div>
			<div class="px-5">
				<div class="self-center text-xm font-medium mr-auto mb-1">Skills evaluated</div>
				<div class="flex flex-col pl-0.5">
					<label class="dark:bg-gray-900 w-fit rounded py-1 text-xs bg-transparent outline-none text-right">
						<input
							type="checkbox"
							on:change={toggleAll}
							checked={selectedEvalSkills.length === skills.length}
						>
						All
					</label>
					{#each skills as skill}
						<label class="dark:bg-gray-900 w-fit rounded py-1 text-xs bg-transparent outline-none text-right">
							<input
								type="checkbox"
								value={skill}
								bind:group={selectedEvalSkills}
							>
							{skill}
						</label>
					{/each}
				</div>
			</div>
			
		</div>

		<div class="flex flex-row-reverse px-5 pb-4">
			<button class="px-4 py-2 bg-emerald-700 hover:bg-emerald-800 text-gray-100 transition rounded-lg"
				on:click={evaluateChatHandler}>
				Evaluate
			</button>
		</div>
	</div>
</Modal>
