<script lang="ts">
	import { WEBUI_BASE_URL } from '$lib/constants';
	import { onMount, getContext } from 'svelte';

	import { toast } from 'svelte-sonner';

	import { getUsers } from '$lib/apis/users';

	import Pagination from '$lib/components/common/Pagination.svelte';
	import SortableHeader from '$lib/components/admin/SortableHeader.svelte';
	import XMark from '../icons/XMark.svelte';
	import { DropdownMenu } from 'bits-ui';
	import { mobile } from '$lib/stores';
	import { flyAndScale } from '$lib/utils/transitions';
	import Search from '../icons/Search.svelte';
	import ImportStudentModal from './ImportStudentModal.svelte';

	const i18n = getContext('i18n');

	let loaded = false;
	let users = [];

	let search = '';
	let page = 1;

	export let searchEnabled = true;
	export let searchPlaceholder = "Search Users";
	export let className = 'w-[16rem]';
    
    let studentShow = false;
    let searchValue = "";

    export let selectedUsers: string[] = [];

    // TODO: change to set if number of students increases
    let _selectedUsers = [];
    let _unselectedUsers = [];

	const sortFactory = (attribute, ascending = true) => {
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

	let sortAttribute = "name";
	let ascending = true;

    let show = false;

    const saveHandler = (event) => {
        const userIds = event.detail;
        const newUsersSet = new Set<string>(userIds).union(new Set(selectedUsers));
        selectedUsers = Array.from(newUsersSet);
    }

	onMount(async () => {
		users = await getUsers(localStorage.token).catch((error) => toast.error(error));
        loaded = true;
	});

    $: if (selectedUsers) {
        _selectedUsers = users.filter((user) => selectedUsers.includes(user.id));
        _unselectedUsers = users.filter((user) => !selectedUsers.includes(user.id));
    };

    $: filteredUsers = searchValue
		? _unselectedUsers.filter((user) => (user.name.toLowerCase() + user.email.toLowerCase()).includes(searchValue.toLowerCase()))
		: _unselectedUsers;
</script>

<ImportStudentModal 
    bind:show
    on:save={saveHandler}/>

<table class="w-full text-sm text-left text-gray-500 dark:text-gray-400 table-auto max-w-full">
    <thead class="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-850 dark:text-gray-400">
        <tr>
            <th scope="col" class="px-3 py-2"> 
                <SortableHeader displayName={$i18n.t('Name')} attributeName="name"
                    bind:currentAttribute={sortAttribute} bind:currentAscending={ascending}/>
            </th>
            <th scope="col" class="px-3 py-2">
                <SortableHeader displayName={$i18n.t('Email')} attributeName="email"
                    bind:currentAttribute={sortAttribute} bind:currentAscending={ascending}/>
            </th>
            <th scope="col" class="px-3 py-2 w-32" />
        </tr>
    </thead>
    <tbody>
        {#each _selectedUsers
            .filter((user) => {
                if (search === '') {
                    return true;
                } else {
                    let name = user.name.toLowerCase();
                    const query = search.toLowerCase();
                    return name.includes(query);
                }
            })
            .slice((page - 1) * 10, page * 10)
            .sort(sortFactory(sortAttribute, ascending)) as user}
            <tr class="bg-white border-b dark:bg-gray-900 dark:border-gray-700 text-xs">
                <td class="px-3 py-2 font-medium text-gray-900 dark:text-white w-max">
                    <div class="flex flex-row w-max">
                        <img
                            class=" rounded-full w-6 h-6 object-cover mr-2.5"
                            src={user.profile_image_url.startsWith(WEBUI_BASE_URL) ||
                            user.profile_image_url.startsWith('https://www.gravatar.com/avatar/') ||
                            user.profile_image_url.startsWith('data:')
                                ? user.profile_image_url
                                : `/user.png`}
                            alt="user"
                        />

                        <div class=" font-medium self-center">{user.name}</div>
                    </div>
                </td>
                <td class=" px-3 py-2"> {user.email} </td>

                <td class="px-3 py-2 text-right w-32">
                    <div class="flex justify-end w-full">
                        <button
                            type="button"
                            class="self-center w-fit text-sm px-2 py-2 hover:bg-black/5 dark:hover:bg-white/5 rounded-lg"
                            on:click={async () => {
                                selectedUsers = selectedUsers.filter(
                                    (selected) => selected !== user.id
                                );
                            }}
                        >
                            <XMark />
                        </button>
                    </div>
                </td>
            </tr>
        {/each}
    </tbody>
</table>

<Pagination bind:page count={users.length} perPage={10} />

<div class="flex flex-row">
    <DropdownMenu.Root
        bind:open={studentShow}
        onOpenChange={async () => {
            searchValue = '';
            window.setTimeout(() => document.getElementById('item-search-input')?.focus(), 0);
        }}
    >
        <DropdownMenu.Trigger aria-label="add-student">
            <button class="text-sm px-3 py-2 transition rounded-xl bg-gray-50 hover:bg-gray-100 dark:bg-gray-700 dark:hover:bg-gray-800"
                type="button"
            >
                <div class="self-center text-sm font-medium text-nowrap">Add Student</div>
            </button>
        </DropdownMenu.Trigger>

        <DropdownMenu.Content
            class=" z-40 {$mobile
                ? `w-full`
                : `${className}`} max-w-[calc(100vw-1rem)] justify-start rounded-xl  bg-white dark:bg-gray-850 dark:text-white shadow-lg border border-gray-300/30 dark:border-gray-700/50  outline-none "
            transition={flyAndScale}
            side={$mobile ? 'bottom' : 'bottom-start'}
            sideOffset={4}
        >
            <slot>
                {#if searchEnabled}
                    <div class="flex items-center gap-2.5 px-5 mt-3.5 mb-3">
                        <Search className="size-4" strokeWidth="2.5" />

                        <input
                            id="item-search-input"
                            bind:value={searchValue}
                            class="w-full text-sm bg-transparent outline-none"
                            placeholder={searchPlaceholder}
                            autocomplete="off"
                        />
                    </div>

                    <hr class="border-gray-100 dark:border-gray-800" />
                {/if}

                <div class="px-3 my-2 max-h-64 overflow-y-auto scrollbar-hidden">
                    {#each filteredUsers as user}
                        <button
                            aria-label="item-item"
                            type="button"
                            class="flex w-full text-left font-medium line-clamp-1 select-none items-center rounded-button py-2 pl-3 pr-1.5 text-sm text-gray-700 dark:text-gray-100 outline-none transition-all duration-75 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg cursor-pointer data-[highlighted]:bg-muted"
                            on:click={() => {
                                selectedUsers = [ ...selectedUsers, user.id ]
                            }}
                        >
                            <div class="flex items-center gap-2">
                                <div class="">
                                    {user.name}

                                    <span class=" text-xs font-medium text-gray-600 dark:text-gray-400"
                                        >{user.email}</span
                                    >
                                </div>
                            </div>
                        </button>
                    {:else}
                        <div class="block px-3 py-2 text-sm text-gray-700 dark:text-gray-100">
                            No results found, add more users under Admin Panel > 
                            <span class="inline-flex">
                                Add Users
                                <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    viewBox="0 0 16 16"
                                    fill="currentColor"
                                    class="ml-1 w-4 h-4 items-baseline"
                                >
                                <path
                                    d="M8.75 3.75a.75.75 0 0 0-1.5 0v3.5h-3.5a.75.75 0 0 0 0 1.5h3.5v3.5a.75.75 0 0 0 1.5 0v-3.5h3.5a.75.75 0 0 0 0-1.5h-3.5v-3.5Z"
                                />
                                </svg>
                            </span>.
                        </div>
                    {/each}
                </div>

                <div class="hidden w-[42rem]" />
                <div class="hidden w-[32rem]" />
            </slot>
        </DropdownMenu.Content>
    </DropdownMenu.Root>

    <button
        class="ml-2 text-sm px-3 py-2 transition rounded-xl bg-gray-50 hover:bg-gray-100 dark:bg-gray-700 dark:hover:bg-gray-800 flex"
        type="button"
        on:click={() => show = !show}
    >
        <div class="self-center font-medium">Import Students</div>
    </button>
</div>

<style>
	.scrollbar-hidden:active::-webkit-scrollbar-thumb,
	.scrollbar-hidden:focus::-webkit-scrollbar-thumb,
	.scrollbar-hidden:hover::-webkit-scrollbar-thumb {
		visibility: visible;
	}
	.scrollbar-hidden::-webkit-scrollbar-thumb {
		visibility: hidden;
	}
</style>