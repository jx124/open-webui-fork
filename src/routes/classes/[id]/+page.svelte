<script lang="ts">
	import { type Class, classes, prompts, WEBUI_NAME } from '$lib/stores';
	import { onMount } from 'svelte';
	import { getClassList } from '$lib/apis/classes';
	import { toast } from 'svelte-sonner';
	import { getPrompts } from '$lib/apis/prompts';
	import { page } from '$app/stores';
	import AcademicWeekDisplay from '$lib/components/classes/AcademicWeekDisplay.svelte';
	import { goto } from '$app/navigation';

	let loading = true;
	let currentClassId: number = parseInt($page.params.id);
	let currentClass: Class;

	onMount(async () => {
		if ($classes.length === 0) {
			$classes = await getClassList(localStorage.token).catch((error) => toast.error(error));
		}
		if ($prompts.length === 0) {
			$prompts = await getPrompts(localStorage.token).catch((error) => toast.error(error));
		}

		const class_ = $classes.find((c) => c.id === currentClassId);
		if (class_ === undefined) {
			await goto("/classes");
		} else {
			currentClass = class_;
		}

		loading = false;
	});
</script>

<svelte:head>
	<title>
		{currentClass?.name} | {$WEBUI_NAME}
	</title>
</svelte:head>

<div class="flex flex-col w-full min-h-screen max-h-screen items-center justify-center">
	<div class="w-1/2 h-3/4">
		<div class=" text-3xl font-semibold mb-3">{currentClass?.name} Assignments</div>

		{#if !loading && currentClass}
			<div class=" my-2 mb-5" id="class-list">
				<AcademicWeekDisplay bind:assignments={currentClass.assignments} bind:currentClassId />
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
