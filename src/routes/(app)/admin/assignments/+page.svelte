<script lang="ts">
	import { getAllChatListsByUserId } from "$lib/apis/chats";
	import { getPromptTitles } from "$lib/apis/prompts";
	import { getUserProfiles } from "$lib/apis/users";
	import ClassSearchbar from "$lib/components/admin/ClassSearchbar.svelte";
	import ProfileSearchbar from "$lib/components/admin/ProfileSearchbar.svelte";
	import SortableHeader from "$lib/components/admin/SortableHeader.svelte";
	import UserAssignmentModal from "$lib/components/admin/UserAssignmentModal.svelte";
	import Pagination from "$lib/components/common/Pagination.svelte";
	import Tooltip from "$lib/components/common/Tooltip.svelte";
	import ChatBubbles from "$lib/components/icons/ChatBubbles.svelte";
	import { WEBUI_BASE_URL } from "$lib/constants";
	import { classes, prompts, WEBUI_NAME } from "$lib/stores";
	import { getContext, onMount } from "svelte";
    
	const i18n = getContext('i18n');
    
    type AssignmentEntry = {
		user_id: string
        user_name: string;
        profile_image_url: string;
        class_id: number;
        class_name: string;
        profile_id: number;
		profile_title: string;
        deadline: string;
        attempts: number;
		submitted: boolean;
    }
    
    let userProfiles: {
        [key: string]: {
            name: string;
            profile_image_url: string;
        }
    } = {};

    let entries: AssignmentEntry[] = [];
    let chats = {};
    let profileTitles;

    let loaded = false;

    let search = "";
	let sortAttribute = "user_name";
	let ascending = true;
    let page = 1;

	let showAssignmentModal = false;
	let selectedChats = [];
	let selectedUserName = "";
	let selectedClassName = "";
	let selectedProfileName = "";

	let classItems: {
		label: string;
		value: number;
	}[] = []
	let selectedClassId = 0;

	let profileItems: {
		label: string;
		value: number;
	}[] = []
	let selectedProfileId = 0;

	let classAssignmentMap = new Map<number, Set<number>>();

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

    onMount(async () => {
		userProfiles = await getUserProfiles(localStorage.token);
        chats = await getAllChatListsByUserId(localStorage.token);
        profileTitles = await getPromptTitles(localStorage.token);

        for (const class_ of $classes) {
			classAssignmentMap.set(class_.id, new Set<number>(class_.assignments.map(a => a.prompt_id)));

            for (const student of class_.assigned_students) {
                for (const assignment of class_.assignments) {
					const chatAttempts = chats[student]?.filter((chat) => 
                            chat.class_id === class_.id && chat.prompt_id === assignment.prompt_id
                        ) ?? [];
                    entries.push({
						user_id: student,
                        user_name: userProfiles[student].name,
                        profile_image_url: userProfiles[student].profile_image_url,
                        class_id: class_.id,
                        class_name: class_.name,
                        profile_id: assignment.prompt_id,
						profile_title: profileTitles[assignment.prompt_id],
                        deadline: assignment.deadline ?? "",
                        attempts: chatAttempts.length,
						submitted: chatAttempts.filter((chat) => chat.is_submitted).length > 0,
                    })
                }
            }
        }

		classItems = [{ label: "All", value: 0 }, ...$classes.map((c) => {
			return {
				label: c.name,
				value: c.id
			}
		})];

		profileItems = [{ label: "All", value: 0 }, ...$prompts.map((c) => {
			return {
				label: c.title,
				value: c.id
			}
		})];

        loaded = true;
    })
</script>

<svelte:head>
	<title>
		Assignments | {$WEBUI_NAME}
	</title>
</svelte:head>

<UserAssignmentModal 
	bind:show={showAssignmentModal}
	bind:chats={selectedChats}
	bind:user_name={selectedUserName}
	bind:class_name={selectedClassName}
	bind:profile_name={selectedProfileName} />

{#if loaded}
	<div class="flex flex-col">
		<div class="flex gap-4">
			<div class="flex flex-col">
				<div class="font-semibold text-sm mb-1">Class Filter</div>
				<ClassSearchbar
					items={classItems}
					bind:value={selectedClassId}
				/>
			</div>
			<div class="flex flex-col">
				<div class="font-semibold text-sm mb-1">Profile Filter</div>
				<ProfileSearchbar
					items={profileItems}
					{classAssignmentMap}
					bind:value={selectedProfileId}
					bind:selectedClassId
				/>
			</div>
			<div class="self-end">
				<button
					class=" text-sm px-3 py-1.5 transition rounded-xl bg-gray-50 hover:bg-gray-100 dark:bg-gray-700 dark:hover:bg-gray-800 flex"
					on:click={() => {
						selectedClassId = 0;
						selectedProfileId = 0;
					}}
					type="button"
				>
					<div class=" self-center font-medium">Reset</div>
				</button>
			</div>
		</div>
	</div>

	<hr class=" my-2 dark:border-gray-850" />

	<div class="mt-0.5 mb-3 gap-1 flex flex-col md:flex-row justify-between">

		<div class="flex md:self-center text-lg font-medium px-0.5">
			Assignments
		</div>

		<div class="flex gap-1">
			<input
				class="w-full md:w-60 rounded-xl py-1.5 px-4 text-sm dark:text-gray-300 dark:bg-gray-850 outline-none"
				placeholder={$i18n.t('Search')}
				bind:value={search}
			/>
		</div>
	</div>

	<div class="scrollbar-hidden relative whitespace-nowrap overflow-x-auto max-w-full">
		<table class="w-full text-sm text-left text-gray-500 dark:text-gray-400 table-auto max-w-full">
			<thead class="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-850 dark:text-gray-400">
				<tr>
					<th scope="col" class="px-3 py-2"> 
						<SortableHeader displayName="Name" attributeName="user_name"
							bind:currentAttribute={sortAttribute} bind:currentAscending={ascending}/>
					</th>
					<th scope="col" class="px-3 py-2">
						<SortableHeader displayName="Class" attributeName="class_name"
							bind:currentAttribute={sortAttribute} bind:currentAscending={ascending}/>
					</th>
					<th scope="col" class="px-3 py-2">
						<SortableHeader displayName="Profile" attributeName="profile_title"
							bind:currentAttribute={sortAttribute} bind:currentAscending={ascending}/>
					</th>
					<th scope="col" class="px-3 py-2">
						<SortableHeader displayName="Deadline" attributeName="deadline"
							bind:currentAttribute={sortAttribute} bind:currentAscending={ascending}/>
					</th>
					<th scope="col" class="px-3 py-2">
						<SortableHeader displayName="Attempts" attributeName="attempts"
							bind:currentAttribute={sortAttribute} bind:currentAscending={ascending}/>
					</th>
					<th scope="col" class="px-3 py-2">
						<SortableHeader displayName="Submitted" attributeName="submitted"
							bind:currentAttribute={sortAttribute} bind:currentAscending={ascending}/>
					</th>

					<th scope="col" class="px-3 py-2 w-32" />
				</tr>
			</thead>
			<tbody>
				{#each entries
					.filter((entry) => {
						if (selectedClassId === 0) {
							return true;
						} else if (selectedClassId !== 0) {
							return entry.class_id === selectedClassId;
						}
					})
					.filter((entry) => {
						if (selectedProfileId === 0) {
							return true;
						} else if (selectedProfileId !== 0) {
							return entry.profile_id === selectedProfileId;
						}
					})
					.filter((entry) => {
						if (search === '') {
							return true;
						} else {
							let name = entry.user_name.toLowerCase();
							const query = search.toLowerCase();
							return name.includes(query);
						}
					})
					.sort(sortFactory(sortAttribute, ascending))
					.slice((page - 1) * 20, page * 20) as entry}
					<tr class="bg-white border-b dark:bg-gray-900 dark:border-gray-700 text-xs">
						<td class="px-3 py-2 font-medium text-gray-900 dark:text-white w-max">
							<div class="flex flex-row w-max">
								<img
									class=" rounded-full w-6 h-6 object-cover mr-2.5"
									src={entry.profile_image_url.startsWith(WEBUI_BASE_URL) ||
									entry.profile_image_url.startsWith('https://www.gravatar.com/avatar/') ||
									entry.profile_image_url.startsWith('data:')
										? entry.profile_image_url
										: `/user.png`}
									alt="user"
								/>

								<div class=" font-medium self-center">{entry.user_name}</div>
							</div>
						</td>
						<td class=" px-3 py-2"> {entry.class_name} </td>
						<td class=" px-3 py-2"> {entry.profile_title} </td>
						<td class=" px-3 py-2"> {entry.deadline ? new Date(entry.deadline).toString().split(" GMT")[0] : "No Deadline"} </td>
						<td class=" px-3 py-2"> {entry.attempts} </td>
						<td class=" px-3 py-2"> {entry.submitted ? "Yes" : "No"} </td>
						<td class="px-3 py-2 text-right w-32">
							<div class="flex justify-end w-full">
								<div class="flex justify-start min-w-24">
									<Tooltip content={$i18n.t('View Attempts')}>
										<button
										class="self-center w-fit text-sm px-2 py-2 hover:bg-black/5 dark:hover:bg-white/5 rounded-xl"
										on:click={() => {
											showAssignmentModal = !showAssignmentModal;
											selectedChats = chats[entry.user_id]?.filter((chat) => {
												return chat.class_id === entry.class_id && chat.prompt_id === entry.profile_id;
											});
											selectedUserName = entry.user_name;
											selectedClassName = entry.class_name;
											selectedProfileName = entry.profile_title;
										}}
											>
											<ChatBubbles />
										</button>
									</Tooltip>
								</div>
							</div>
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>

	<div class=" text-gray-500 text-xs mt-2 text-left">
		ⓘ Statistics are estimates and do not include usage before tracking was enabled.  <br />
		ⓘ To enable tracking, go to Admin Panel > Models, select the model, check "Usage" under "Capabilities", and save the configuration.
	</div>

	<Pagination bind:page count={entries.length} />
{/if}