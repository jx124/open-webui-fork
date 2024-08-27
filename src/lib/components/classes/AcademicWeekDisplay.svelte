<script lang="ts">
	import { getAssignmentSubmissions, type Assignment } from '$lib/apis/classes';
	import { prompts, type Prompt } from '$lib/stores';
	import NUSModerator from 'nusmoderator';
	import { onMount } from 'svelte';

	export let assignments: Assignment[] = [];
	export let currentClassId: number;

	let submitted: {
		[key: number]: boolean;
	} = {};

	let noDeadlineIds: number[] = [];
	let sortedDeadlineIds: number[] = [];
	let profileDeadlineMap: Map<number, string | null> = new Map();

	let noDeadlineProfiles: Prompt[] = [];
	let sortedDeadlineProfiles: Prompt[] = [];
	let weekProfilesMap: Map<string, Prompt[]> = new Map();
	let weeks: string[] = [];

	const getNUSWeekName = (date: string) => {
		if (date === '') {
			return '';
		}
		const week = NUSModerator.academicCalendar.getAcadWeekInfo(new Date(date ?? ''));

		if (week === null) {
			return 'Others';
		}

		if (week.type === 'Instructional') {
			return 'Week ' + (week.num ?? 0);
		} else {
			return week.type + ' Week ' + (week.num ?? '');
		}
	};

	const dateSorter = (a: Assignment, b: Assignment) => {
		if (a.deadline === null || b.deadline === null) {
			return 0;
		}
		return new Date(a.deadline).getTime() < new Date(b.deadline).getTime() ? -1 : 1;
	};

	onMount(async () => {
		submitted = await getAssignmentSubmissions(localStorage.token, currentClassId).catch((error) => toast.error(error));
		console.log("submitted", submitted);
		
		noDeadlineIds = assignments.filter((p) => p.deadline === null).map(a => a.prompt_id);
		sortedDeadlineIds = assignments.filter((p) => p.deadline !== null).sort(dateSorter).map(a => a.prompt_id);
		
		// TODO: use maps if performance not good enough
		noDeadlineProfiles = noDeadlineIds.map(id => $prompts.find(p => p.id === id));
		sortedDeadlineProfiles = sortedDeadlineIds.map(id => $prompts.find(p => p.id === id));

		for (const assignment of assignments) {
			profileDeadlineMap.set(assignment.prompt_id, assignment.deadline);
		}

		for (const profile of sortedDeadlineProfiles) {
			const name = getNUSWeekName(profileDeadlineMap.get(profile.id) ?? '');

			if (weekProfilesMap.get(name)) {
				weekProfilesMap.get(name)?.push(profile);
			} else {
				weekProfilesMap.set(name, [profile]);
				weeks.push(name);
			}
		}
		weeks = weeks;
	});
</script>

{#each noDeadlineProfiles as profile}
	<div
		class="flex flex-col mb-10 text-black dark:text-white font-semibold border dark:border-gray-600 rounded-md outline-none overflow-hidden"
	>
		<div class="flex px-5 py-2 bg-gray-100 dark:bg-gray-800">No Deadline</div>
		<div
			class=" flex space-x-4 cursor-pointer w-full px-3 py-2 dark:hover:bg-white/5 hover:bg-black/5"
		>
			<div class="flex flex-1 space-x-4 cursor-pointer w-full">
				<a
					class="flex items-center"
					href={`/c/?profile=${encodeURIComponent(profile.command)}` +
						`&model=${encodeURIComponent(profile.selected_model_id)}` +
						`&class=${currentClassId}`}
				>
					<img
						src={profile.image_url ? profile.image_url : '/user.png'}
						alt="profile"
						class="rounded-full h-16 w-16 object-cover"
					/>
					<div class=" flex-1 self-center pl-3">
						<div class=" font-bold">
							{profile.title}
						</div>
					</div>
				</a>
			</div>
		</div>
	</div>
{/each}

{#each weeks as week}
	<div
		class="flex flex-col mb-10 text-black dark:text-white font-semibold border dark:border-gray-600 rounded-md outline-none overflow-hidden"
	>
		<div class="flex px-5 py-2 text-black dark:text-white bg-gray-100 dark:bg-gray-800">{week}</div>
		{#each weekProfilesMap.get(week) ?? [] as profile}
			<div
				class=" flex space-x-4 cursor-pointer w-full px-3 py-2 dark:hover:bg-white/5 hover:bg-black/5"
			>
				<div class="flex flex-1 space-x-4 cursor-pointer w-full">
					<a
						class="flex items-center"
						href={`/c/?profile=${encodeURIComponent(profile.command)}` +
							`&model=${encodeURIComponent(profile.selected_model_id)}` +
							`&class=${currentClassId}`}
					>
						<img
							src={profile.image_url ? profile.image_url : '/user.png'}
							alt="profile"
							class="rounded-full h-16 w-16 object-cover"
						/>
						<div class=" flex-1 self-center pl-3">
							<div class=" font-bold">
								{profile.title}
							</div>
							{#if profileDeadlineMap.get(profile.id)}
								<div class="text-xs text-gray-600 dark:text-gray-400">
									Due: {new Date(profileDeadlineMap.get(profile.id) ?? "").toString()}
								</div>
								<div class="text-xs">
									{submitted[profile.id] ? "Submitted" : "Not Submitted"}
								</div>
							{/if}
						</div>
					</a>
				</div>
			</div>
		{/each}
	</div>
{/each}
