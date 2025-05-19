<script lang="ts">
	import { type Class, classes, classId, chats, prompts, WEBUI_NAME } from '$lib/stores';
	import { onMount, getContext } from 'svelte';
	import { getClassList } from '$lib/apis/classes';
	import { toast } from 'svelte-sonner';
	import { getPrompts } from '$lib/apis/prompts';
	import { getAssignmentSubmissions } from '$lib/apis/classes';
	import { getAllChats, getChatList } from '$lib/apis/chats';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import SortableHeader from '$lib/components/admin/SortableHeader.svelte';
	import Pagination from '$lib/components/common/Pagination.svelte';

	let currentClassId: number = parseInt($page.params.id);
	let currentClass: Class;

    let assignment;
    const prompt_id = parseInt($page.params.prompt_id);

	import dayjs from 'dayjs';

	const i18n = getContext('i18n');

	let loaded = false;
    let search = '';

	let pageNumber = 1;

	const sortFactory = (attribute: string, ascending = true) => {
		return (a, b) => {
			const aValue = a[attribute].toLowerCase?.() ?? a[attribute];
			const bValue = b[attribute].toLowerCase?.() ?? b[attribute];
			if (aValue < bValue) {
				return ascending ? -1 : 1;
			}
			if (aValue > bValue) {
				return ascending ? 1 : -1;
			}
			return 0;
		}
	}

	let sortAttribute = "status";
	let ascending = true;
    let attempts = [];

	onMount(async () => {
		if ($classes.length === 0) {
			$classes = await getClassList(localStorage.token).catch((error) => toast.error(error));
		}
		if ($prompts.length === 0) {
			$prompts = await getPrompts(localStorage.token).catch((error) => toast.error(error));
		}
        $chats = await getAllChats(localStorage.token);

		const class_ = $classes.find((c) => c.id === currentClassId);

		if (class_ === undefined) {
            toast.error("Class not found");
			await goto("/classes");
            return;
		} else {
			currentClass = class_;
            $classId = currentClassId;
		}

        assignment = currentClass.assignments.find((assignment) => assignment.prompt_id === prompt_id);
		if (assignment === undefined) {
            toast.error("Assignment not found");
			await goto("/classes/" + $classId);
            return;
        }

        attempts = $chats.filter((chat) => chat.prompt_id === prompt_id);

        for (let attempt of attempts) {
            if (attempt.is_submitted) {
                attempt.status = "Submitted";
            } else {
                if (assignment.allow_submit_after_deadline || (assignment.deadline && (new Date() <= new Date(assignment.deadline)))) {
                    attempt.status = "In Progress"
                } else {
                    attempt.status = "Locked"
                }
            }
        }

		loaded = true;
	});
</script>

<svelte:head>
	<title>
		{$prompts.find((prompt) => prompt.id === prompt_id)?.title} Attempts | {$WEBUI_NAME}
	</title>
</svelte:head>

{#if loaded}
    <div class="px-5 py-1">
        <div class="mt-0.5 mb-3 gap-1 flex flex-col md:flex-row justify-between">
            <div class="flex flex-col md:self-center text-lg font-medium px-0.5">
                {$prompts.find((prompt) => prompt.id === prompt_id)?.title} Attempts
                <input
                    class="w-full md:w-60 rounded-xl mt-3 mb-1 py-1.5 px-4 text-sm dark:text-gray-300 bg-gray-100 dark:bg-gray-850 outline-none"
                    placeholder={$i18n.t('Search')}
                    bind:value={search}
                />
            </div>
        </div>

        <div class="scrollbar-hidden relative whitespace-nowrap overflow-x-auto max-w-full">
            <table class="w-full text-sm text-left text-gray-800 dark:text-gray-400 table-auto max-w-full">
                <thead class="text-xs text-gray-700 uppercase bg-gray-100 dark:bg-gray-850 dark:text-gray-400">
                    <tr>
                        <th scope="col" class="px-3 py-2 w-32"> 
                            <SortableHeader displayName={"Status"} attributeName="status"
                                bind:currentAttribute={sortAttribute} bind:currentAscending={ascending}/>
                        </th>
                        <th scope="col" class="px-3 py-2 w-2/5">
                            <SortableHeader displayName={"Title"} attributeName="title"
                                bind:currentAttribute={sortAttribute} bind:currentAscending={ascending}/>
                        </th>
                        <th scope="col" class="px-3 py-2">
                            <SortableHeader displayName={"Deadline"} attributeName="deadline"
                                bind:currentAttribute={sortAttribute} bind:currentAscending={ascending}/>
                        </th>

                        <th scope="col" class="px-3 py-2 w-32" >
                            Actions
                        </th>
                    </tr>
                </thead>
                <tbody>
                    {#each attempts
                        .filter((attempt) => {
                            if (search === '') {
                                return true;
                            } else {
                                let title = attempt.title.toLowerCase();
                                const query = search.toLowerCase();
                                return title.includes(query);
                            }
                        })
                        .sort(sortFactory(sortAttribute, ascending))
                        .slice((pageNumber - 1) * 20, pageNumber * 20) as attempt}
                        <tr class="bg-white border-b dark:bg-gray-900 dark:border-gray-700">
                            <td class="px-3 py-2 w-32">
                                <div class="flex">
                                    {#if attempt.status === "Submitted"}
                                        <div class="flex w-20 items-center justify-center gap-2 text-xs px-3 py-0.5 rounded-lg bg-green-200 dark:bg-green-800/50 text-green-900 dark:text-green-100">
                                            Submitted
                                        </div>
                                    {:else if attempt.status === "In Progress"}
                                        <div class="flex w-20 items-center justify-center gap-2 text-xs px-3 py-0.5 rounded-lg bg-yellow-200 dark:bg-yellow-400/50 text-yellow-900 dark:text-yellow-100">
                                            In Progress
                                        </div>
                                    {:else}
                                        <div class="flex w-20 items-center justify-center gap-2 text-xs px-3 py-0.5 rounded-lg bg-red-200 dark:bg-red-800/50 text-red-900 dark:text-red-100">
                                            Locked
                                        </div>
                                    {/if}
                                </div>
                            </td>
                            <td class="px-3 py-2 min-w-[7rem] w-2/5">
                                {attempt.title}
                            </td>

                            <td class=" px-3 py-2">
                                {attempt.deadline ? dayjs(attempt.deadline).format($i18n.t('HH:mm, MMMM DD, YYYY')) : "-"}
                            </td>

                            <td class=" px-3 py-2">
                                <a href="/c/{attempt.id}">
                                    <button 
                                        class="flex w-16 items-center justify-center gap-2 text-xs px-3 py-0.5 rounded-lg bg-gray-200 hover:bg-gray-300 
                                               dark:bg-gray-700 dark:hover:bg-gray-800 dark:text-gray-100 text-gray-900"
                                    >
                                        View
                                    </button>
                                </a>
                            </td>
                        </tr>
                    {/each}
                </tbody>
            </table>
        </div>

        <Pagination page={pageNumber} count={attempts.length} />
    </div>
{/if}
