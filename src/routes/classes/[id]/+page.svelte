<script lang="ts">
	import { classes, prompts, WEBUI_NAME } from '$lib/stores';
	import { onMount } from 'svelte';
	import { getClassList } from '$lib/apis/classes';
	import { toast } from 'svelte-sonner';
	import { getPrompts } from '$lib/apis/prompts';
	import { page } from '$app/stores';

	let searchValue = '';
	let loading = true;
	let currentClassId: number = parseInt($page.params.id);
	let currentClass;

	let assignedPromptIds: Set<number>;
    let assignedPrompts;

	onMount(async () => {
		console.log("/classes/[id] page");
		if ($classes.length === 0) {
			$classes = await getClassList(localStorage.token).catch((error) => toast.error(error));
		}
		if ($prompts.length === 0) {
			$prompts = await getPrompts(localStorage.token).catch((error) => toast.error(error));
		}

		currentClass = $classes.find((c) => c.id === currentClassId);
		assignedPromptIds = new Set<number>(currentClass?.assigned_prompts ?? []);
        assignedPrompts = $prompts.filter((p) => assignedPromptIds.has(p.id));

		loading = false;
	});
</script>

<svelte:head>
	<title>
		{currentClass?.name} | {$WEBUI_NAME}
	</title>
</svelte:head>

<div class="flex flex-col w-full min-h-screen max-h-screen items-center justify-center">
	<div class=" h-1/2 w-1/2 overflow-y-auto">
		<div class=" text-3xl font-semibold mb-3">{currentClass?.name} Profiles</div>

		<div class="flex w-full space-x-2 mb-2">
			<div class="flex flex-1 px-3 py-1.5 border dark:border-gray-600 outline-none rounded-lg">
				<div class=" self-center ml-1 mr-3">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						viewBox="0 0 20 20"
						fill="currentColor"
						class="w-4 h-4"
					>
						<path
							fill-rule="evenodd"
							d="M9 3.5a5.5 5.5 0 100 11 5.5 5.5 0 000-11zM2 9a7 7 0 1112.452 4.391l3.328 3.329a.75.75 0 11-1.06 1.06l-3.329-3.328A7 7 0 012 9z"
							clip-rule="evenodd"
						/>
					</svg>
				</div>
				<input
					class=" w-full text-sm pr-4 py-1 rounded-r-xl outline-none bg-transparent"
					bind:value={searchValue}
					placeholder={'Search Profiles'}
				/>
			</div>
		</div>

		{#if !loading}
			<div class=" my-2 mb-5" id="class-list">
				{#each assignedPrompts.filter((p) => searchValue === '' || p.title
							.toLowerCase()
							.includes(searchValue) || p.command.toLowerCase().includes(searchValue)) as prompt}
					<div
						class=" flex space-x-4 cursor-pointer w-full px-3 py-2 dark:hover:bg-white/5 hover:bg-black/5 rounded-xl"
					>
						<div class="flex flex-1 space-x-4 cursor-pointer w-full">
							<a
								class="flex items-center"
								href={`/c/?profile=${encodeURIComponent(prompt.command)}&model=${encodeURIComponent(prompt.selected_model_id)}`}
							>
								<img
									src={prompt.image_url ? prompt.image_url : '/user.png'}
									alt="profile"
									class="rounded-full h-16 w-16 object-cover"
								/>
								<div class=" flex-1 self-center pl-3">
									<div class=" font-bold">
										{prompt.title}
									</div>
									{#if prompt.deadline}
										<div class="text-xs text-gray-400 dark:text-gray-500">
											Due: {new Date(prompt.deadline).toString()}
										</div>
									{/if}
								</div>
							</a>
						</div>
					</div>
				{:else}
					<div class="px-2">No profiles found.</div>
				{/each}
			</div>
		{:else}
			<div class="px-2 flex items-center space-x-1">
				<svg
					class=" w-4 h-4"
					viewBox="0 0 24 24"
					fill="currentColor"
					xmlns="http://www.w3.org/2000/svg"
				>
					<style>
						.spinner_ajPY {
							transform-origin: center;
							animation: spinner_AtaB 0.75s infinite linear;
						}
						@keyframes spinner_AtaB {
							100% {
								transform: rotate(360deg);
							}
						}
					</style>
					<path
						d="M12,1A11,11,0,1,0,23,12,11,11,0,0,0,12,1Zm0,19a8,8,0,1,1,8-8A8,8,0,0,1,12,20Z"
						opacity=".25"
					/>
					<path
						d="M10.14,1.16a11,11,0,0,0-9,8.92A1.59,1.59,0,0,0,2.46,12,1.52,1.52,0,0,0,4.11,10.7a8,8,0,0,1,6.66-6.61A1.42,1.42,0,0,0,12,2.69h0A1.57,1.57,0,0,0,10.14,1.16Z"
						class="spinner_ajPY"
					/>
				</svg>
				<span> Loading... </span>
			</div>
		{/if}
	</div>
</div>
