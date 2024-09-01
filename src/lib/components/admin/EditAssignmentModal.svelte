<script lang="ts">
	import { toast } from 'svelte-sonner';

	import Modal from '../common/Modal.svelte';
	import XMark from '../icons/XMark.svelte';
	import DatePicker from '../common/DatePicker.svelte';
	import NUSModerator from 'nusmoderator';
	import { type Assignment } from '$lib/apis/classes';
	import { prompts } from '$lib/stores';

	export let show = false;
    export let assignments: Assignment[] = [];
    export let selectedPromptId: number;
    let index: number;

    $: if (show) {
        index = assignments.findIndex((assignment) => assignment.prompt_id === selectedPromptId);
        selectedDateTime = assignments[index].deadline;
        hasDeadline = assignments[index]?.deadline !== null;
        profileName = $prompts.find((p) => p.id === assignments[index].prompt_id)?.title ?? "";
    }

	let selectedDateTime: string | null = null;
    let hasDeadline = false;
    let profileName = "";

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

	const closeHandler = () => {
        if ((assignments[index].deadline ?? null) === null && hasDeadline === true) {
            toast.error("Select a date for the deadline")
        } else {
            show = false;
        }
	};
</script>

<Modal size="sm" bind:show>
	<div>
		<div class="flex justify-between dark:text-gray-300 px-5 pt-4 pb-2">
			<div class=" text-lg font-medium self-center">Edit Assignment for "{profileName}"</div>
			<button
				class="self-center"
                type="button"
				on:click={closeHandler}
			>
				<XMark />
			</button>
		</div>

        <div class="flex flex-col max-w-2xl mx-auto px-5" >
            <div class="my-2">
                <div class=" text-sm font-semibold mb-1">Multiple Attempts</div>
                <label
                    class="dark:bg-gray-900 w-fit rounded py-1 text-xs bg-transparent outline-none text-right"
                >
                    <input
                        type="checkbox"
                        on:change={() => {
                            assignments[index].allow_multiple_attempts = !assignments[index].allow_multiple_attempts;
                        }}
                        checked={assignments[index].allow_multiple_attempts}
                    />
                    Allow multiple chat attempts.
                </label>
            </div>

            <div class="my-2">
                <div class=" text-sm font-semibold mb-1">Deadline</div>
                <div class="flex flex-col">
                    <label
                        class="dark:bg-gray-900 w-fit rounded py-1 text-xs bg-transparent outline-none text-right"
                    >
                        <input
                            type="checkbox"
                            on:change={() => {
                                if ((assignments[index]?.deadline ?? null) === null) {
                                    hasDeadline = true;
                                } else {
                                    hasDeadline = false;
                                    assignments[index].deadline = null;
                                }
                            }}
                            checked={assignments[index].deadline !== null}
                        />
                        Set deadline for completion.
                    </label>
    
                    {#if hasDeadline}
                        <label
                            class="dark:bg-gray-900 w-fit rounded py-1 text-xs bg-transparent outline-none text-right"
                        >
                            <input
                                type="checkbox"
                                on:change={() => {
                                    assignments[index].allow_submit_after_deadline = !assignments[index].allow_submit_after_deadline;
                                }}
                                checked={assignments[index].allow_submit_after_deadline}
                            />
                            Allow submission after deadline.
                        </label>
                        <DatePicker bind:selectedDateTime={assignments[index].deadline} placeholder={selectedDateTime} />
                        {#if assignments[index].deadline}
                            <div class="text-xs pl-1 pt-1">
                                {assignments[index].deadline ? getNUSWeekName(assignments[index].deadline) : ''}
                            </div>
                        {:else}
                            <div class="text-xs py-2.5" />
                        {/if}
                    {/if}
                </div>
            </div>

            <div class="flex justify-end pb-4 text-sm font-medium">
                <button
                    class=" px-4 py-2 bg-emerald-700 hover:bg-emerald-800 text-gray-100 transition rounded-lg flex flex-row space-x-1 items-center"
                    type="button"
                    on:click={closeHandler}
                >
                    Apply
                </button>
            </div>
        </div>

	</div>
</Modal>