<script lang="ts">
	import { WEBUI_NAME, classId, classes, chats, showSidebar } from '$lib/stores';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { onMount, getContext } from 'svelte';

	import dayjs from 'dayjs';
	import relativeTime from 'dayjs/plugin/relativeTime';
	dayjs.extend(relativeTime);

	import { toast } from 'svelte-sonner';

	import Pagination from '$lib/components/common/Pagination.svelte';
	import SortableHeader from '$lib/components/admin/SortableHeader.svelte';

	import { getAssignmentSubmissions } from '$lib/apis/classes';
	import { getAllChats, getChatList } from '$lib/apis/chats';

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

	let sortAttribute = "updated_at";
	let ascending = true;
    let promptIdSubmittedMap: {
        [key: number]: boolean;
    } = {};

    let chatsInCurrentClass = [];

	let currentClass: Class;
    $: {
        const class_ = $classes.find((c) => c.id === $classId);
		currentClass = class_;
    }

	onMount(async () => {
		promptIdSubmittedMap = await getAssignmentSubmissions(localStorage.token, parseInt($page.params.id)).catch((error) => toast.error(error));
        $chats = await getAllChats(localStorage.token);

        $classId = parseInt($page.params.id)
        localStorage.setItem("classId", $classId.toString());

		const class_ = $classes.find((c) => c.id === $classId);
		if (class_ === undefined) {
            toast.error("Class not found");
			await goto("/classes");
		} else {
			currentClass = class_;
		}

        chatsInCurrentClass = $chats.filter((chat) => chat.class_id === $classId);

        $showSidebar = true;
		
		loaded = true;
	});
</script>

<svelte:head>
	<title>
		{currentClass?.name} Submissions | {$WEBUI_NAME}
	</title>
</svelte:head>

{#if loaded}
    <div class="px-5 py-1">
        <div class="mt-0.5 mb-3 gap-1 flex flex-col md:flex-row justify-between">
            <div class="flex flex-col md:self-center text-lg font-medium px-0.5">
                {currentClass?.name} Submissions
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
                        <th scope="col" class="px-3 py-2"> 
                            <SortableHeader displayName={"Status"} attributeName="is_submitted"
                                bind:currentAttribute={sortAttribute} bind:currentAscending={ascending}/>
                        </th>
                        <th scope="col" class="px-3 py-2 w-2/5">
                            <SortableHeader displayName={"Title"} attributeName="title"
                                bind:currentAttribute={sortAttribute} bind:currentAscending={ascending}/>
                        </th>
                        <th scope="col" class="px-3 py-2">
                            <SortableHeader displayName={"Submitted At"} attributeName="updated_at"
                                bind:currentAttribute={sortAttribute} bind:currentAscending={ascending}/>
                        </th>

                        <th scope="col" class="px-3 py-2 w-32" >
                            Actions
                        </th>
                    </tr>
                </thead>
                <tbody>
                    {#each chatsInCurrentClass
                        .filter((chat) => chat.is_submitted)
                        .filter((chat) => {
                            if (search === '') {
                                return true;
                            } else {
                                let name = chat.name.toLowerCase();
                                const query = search.toLowerCase();
                                return name.includes(query);
                            }
                        })
                        .sort(sortFactory(sortAttribute, ascending))
                        .slice((pageNumber - 1) * 20, pageNumber * 20) as chat}
                        <tr class="bg-white border-b dark:bg-gray-900 dark:border-gray-700 w-32">
                            <td class="px-3 py-2">
                                <div class="flex">
                                    <div class="flex items-center gap-2 text-xs px-3 py-0.5 rounded-lg bg-green-200 dark:bg-green-800/50 text-green-900 dark:text-green-100">
                                        Submitted
                                    </div>
                                </div>
                            </td>
                            <td class="px-3 py-2 min-w-[7rem] w-2/5">
                                {chat.title}
                            </td>

                            <td class=" px-3 py-2">
                                {dayjs(chat.updated_at * 1000).format($i18n.t('HH:mm, MMMM DD, YYYY'))}
                            </td>

                            <td class=" px-3 py-2">
                                <a href="/c/{chat.id}">
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

        <Pagination page={pageNumber} count={chatsInCurrentClass.length} />
    </div>
{/if}
