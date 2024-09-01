<script lang="ts">
	import { WEBUI_BASE_URL } from '$lib/constants';
	import { user, userRoles, classes, WEBUI_NAME } from '$lib/stores';
	import { onMount, getContext } from 'svelte';

	import dayjs from 'dayjs';
	import relativeTime from 'dayjs/plugin/relativeTime';
	dayjs.extend(relativeTime);

	import { toast } from 'svelte-sonner';

	import { updateUserRole, getUsers, deleteUserById, getUserStatistics } from '$lib/apis/users';

	import EditUserModal from '$lib/components/admin/EditUserModal.svelte';
	import SettingsModal from '$lib/components/admin/SettingsModal.svelte';
	import Pagination from '$lib/components/common/Pagination.svelte';
	import ChatBubbles from '$lib/components/icons/ChatBubbles.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import UserChatsModal from '$lib/components/admin/UserChatsModal.svelte';
	import AddUserModal from '$lib/components/admin/AddUserModal.svelte';
	import DeleteModal from '$lib/components/DeleteModal.svelte';
	import RoleSelector from '$lib/components/admin/RoleSelector.svelte';
	import { getRoles } from '$lib/apis/roles';
	import { approximateToHumanReadable } from '$lib/utils';
	import SortableHeader from '$lib/components/admin/SortableHeader.svelte';
	import ClassSearchbar from '$lib/components/admin/ClassSearchbar.svelte';

	const i18n = getContext('i18n');

	let loaded = false;

	let users = [];
	let userStatistics: {
		[key: string]: {
			token_count: number,
			attempts: number,
			session_time: number,
		}
	} = {};

	let search = '';
	let selectedUser = null;

	let page = 1;

	let showSettingsModal = false;
	let showAddUserModal = false;

	let showUserChatsModal = false;
	let showEditUserModal = false;

	let showDeleteModal = false;

	let classItems: {
		label: string;
		value: number;
	}[] = []
	let selectedClass = 0;

	const updateRoleHandler = async (id, role) => {
		const res = await updateUserRole(localStorage.token, id, role).catch((error) => {
			toast.error(error);
			return null;
		});

		if (res) {
			users = await getUsers(localStorage.token);
			users = users.map((user) => {
				return { ...user, ...userStatistics[user?.id] };
			});
		}
	};

	const deleteUserHandler = async (id) => {
		showDeleteModal = false;
		const res = await deleteUserById(localStorage.token, id).catch((error) => {
			toast.error(error);
			return null;
		});
		if (res) {
			users = await getUsers(localStorage.token);
			users = users.map((user) => {
				return { ...user, ...userStatistics[user?.id] };
			});
		}
	};

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

	let sortAttribute = "role";
	let ascending = true;

	let classStudentHashSet = new Map<number, Set<string>>();

	onMount(async () => {
		users = await getUsers(localStorage.token);
		userStatistics = await getUserStatistics(localStorage.token);

		users = users.map((user) => {
			return { ...user, ...userStatistics[user?.id] };
		});

		$userRoles = await getRoles(localStorage.token);

		classItems = [{ label: "All", value: 0 }, ...$classes.map((c) => {
			return {
				label: c.name,
				value: c.id
			}
		})];

		for (const class_ of $classes) {
			classStudentHashSet.set(class_.id, new Set(class_.assigned_students));
		}
		
		loaded = true;
	});

	$: if ($userRoles) {
		// update role displayed when roles are edited
		getUsers(localStorage.token).then((res) => {
			users = res.map((user) => {
				return { ...user, ...userStatistics[user?.id] };
			});
		});
	}
</script>

<svelte:head>
	<title>
		Users | {$WEBUI_NAME}
	</title>
</svelte:head>

{#key selectedUser}
	<EditUserModal
		bind:show={showEditUserModal}
		{selectedUser}
		sessionUser={$user}
		on:save={async () => {
			users = await getUsers(localStorage.token);
		}}
	/>
{/key}

<AddUserModal
	bind:show={showAddUserModal}
	on:save={async () => {
		const temp_users = await getUsers(localStorage.token);
		userStatistics = await getUserStatistics(localStorage.token);

		users = temp_users.map((user) => {
			return { ...user, ...userStatistics[user?.id] };
		});
	}}
/>
<UserChatsModal bind:show={showUserChatsModal} user={selectedUser} />
<SettingsModal bind:show={showSettingsModal} />
<DeleteModal bind:show={showDeleteModal}
	deleteMessage={selectedUser?.name}
	deleteHandler={deleteUserHandler}
	deleteArgs={selectedUser?.id}/>

{#if loaded}
	<div class="flex flex-col">
		<div class="font-semibold text-sm mb-1">Class Filter</div>
		<div class="flex gap-4">
			<div class="flex flex-col">
				<ClassSearchbar
					bind:items={classItems}
					bind:value={selectedClass}
				/>
			</div>
			<div class="self-end">
				<button
					class=" text-sm px-3 py-1.5 transition rounded-xl bg-gray-50 hover:bg-gray-100 dark:bg-gray-700 dark:hover:bg-gray-800 flex"
					on:click={() => {
						selectedClass = 0;
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
			{selectedClass === 0 ? $i18n.t('All Users') : classItems.find(c => c.value === selectedClass)?.label}
			<div class="flex self-center w-[1px] h-6 mx-2.5 bg-gray-200 dark:bg-gray-700" />
			<span class="text-lg font-medium text-gray-500 dark:text-gray-300">
				{selectedClass === 0 ? users.length : classStudentHashSet.get(selectedClass)?.size}
			</span>
		</div>

		<div class="flex gap-1">
			<input
				class="w-full md:w-60 rounded-xl py-1.5 px-4 text-sm dark:text-gray-300 dark:bg-gray-850 outline-none"
				placeholder={$i18n.t('Search')}
				bind:value={search}
			/>

			<div class="flex gap-0.5">
				<Tooltip content="Add User">
					<button
						class=" px-2 py-2 rounded-xl border border-gray-200 dark:border-gray-600 dark:border-0 hover:bg-gray-100 dark:bg-gray-850 dark:hover:bg-gray-800 transition font-medium text-sm flex items-center space-x-1"
						on:click={() => {
							showAddUserModal = !showAddUserModal;
						}}
					>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							viewBox="0 0 16 16"
							fill="currentColor"
							class="w-4 h-4"
						>
							<path
								d="M8.75 3.75a.75.75 0 0 0-1.5 0v3.5h-3.5a.75.75 0 0 0 0 1.5h3.5v3.5a.75.75 0 0 0 1.5 0v-3.5h3.5a.75.75 0 0 0 0-1.5h-3.5v-3.5Z"
							/>
						</svg>
					</button>
				</Tooltip>

				<Tooltip content={$i18n.t('Admin Settings')}>
					<button
						class=" px-2 py-2 rounded-xl border border-gray-200 dark:border-gray-600 dark:border-0 hover:bg-gray-100 dark:bg-gray-850 dark:hover:bg-gray-800 transition font-medium text-sm flex items-center space-x-1"
						on:click={() => {
							showSettingsModal = !showSettingsModal;
						}}
					>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							viewBox="0 0 16 16"
							fill="currentColor"
							class="w-4 h-4"
						>
							<path
								fill-rule="evenodd"
								d="M6.955 1.45A.5.5 0 0 1 7.452 1h1.096a.5.5 0 0 1 .497.45l.17 1.699c.484.12.94.312 1.356.562l1.321-1.081a.5.5 0 0 1 .67.033l.774.775a.5.5 0 0 1 .034.67l-1.08 1.32c.25.417.44.873.561 1.357l1.699.17a.5.5 0 0 1 .45.497v1.096a.5.5 0 0 1-.45.497l-1.699.17c-.12.484-.312.94-.562 1.356l1.082 1.322a.5.5 0 0 1-.034.67l-.774.774a.5.5 0 0 1-.67.033l-1.322-1.08c-.416.25-.872.44-1.356.561l-.17 1.699a.5.5 0 0 1-.497.45H7.452a.5.5 0 0 1-.497-.45l-.17-1.699a4.973 4.973 0 0 1-1.356-.562L4.108 13.37a.5.5 0 0 1-.67-.033l-.774-.775a.5.5 0 0 1-.034-.67l1.08-1.32a4.971 4.971 0 0 1-.561-1.357l-1.699-.17A.5.5 0 0 1 1 8.548V7.452a.5.5 0 0 1 .45-.497l1.699-.17c.12-.484.312-.94.562-1.356L2.629 4.107a.5.5 0 0 1 .034-.67l.774-.774a.5.5 0 0 1 .67-.033L5.43 3.71a4.97 4.97 0 0 1 1.356-.561l.17-1.699ZM6 8c0 .538.212 1.026.558 1.385l.057.057a2 2 0 0 0 2.828-2.828l-.058-.056A2 2 0 0 0 6 8Z"
								clip-rule="evenodd"
							/>
						</svg>
					</button>
				</Tooltip>
			</div>
		</div>
	</div>

	<div class="scrollbar-hidden relative whitespace-nowrap overflow-x-auto max-w-full">
		<table class="w-full text-sm text-left text-gray-500 dark:text-gray-400 table-auto max-w-full">
			<thead class="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-850 dark:text-gray-400">
				<tr>
					<th scope="col" class="px-3 py-2">
						<SortableHeader displayName={$i18n.t('Role')} attributeName="role"
							bind:currentAttribute={sortAttribute} bind:currentAscending={ascending}/>
					</th>
					<th scope="col" class="px-3 py-2"> 
						<SortableHeader displayName={$i18n.t('Name')} attributeName="name"
							bind:currentAttribute={sortAttribute} bind:currentAscending={ascending}/>
					</th>
					<th scope="col" class="px-3 py-2">
						<SortableHeader displayName={$i18n.t('Email')} attributeName="email"
							bind:currentAttribute={sortAttribute} bind:currentAscending={ascending}/>
					</th>
					<th scope="col" class="px-3 py-2">
						<SortableHeader displayName={$i18n.t('Last Active')} attributeName="last_active_at"
							bind:currentAttribute={sortAttribute} bind:currentAscending={ascending}/>
					</th>
					<th scope="col" class="px-3 py-2">
						<SortableHeader displayName={$i18n.t('Created at')} attributeName="created_at"
							bind:currentAttribute={sortAttribute} bind:currentAscending={ascending}/>
					</th>
					<th scope="col" class="px-3 py-2">
						<SortableHeader displayName="Tokens Used" attributeName="token_count"
							bind:currentAttribute={sortAttribute} bind:currentAscending={ascending}/>
					</th>
					<th scope="col" class="px-3 py-2">
						<SortableHeader displayName="Chat Attempts" attributeName="attempts"
							bind:currentAttribute={sortAttribute} bind:currentAscending={ascending}/>
					</th>
					<th scope="col" class="px-3 py-2">
						<SortableHeader displayName="Total Chat Session Time" attributeName="session_time"
							bind:currentAttribute={sortAttribute} bind:currentAscending={ascending}/>
					</th>

					<th scope="col" class="px-3 py-2 w-32" />
				</tr>
			</thead>
			<tbody>
				{#each users
					.filter((user) => {
						if (selectedClass === 0) {
							return true;
						} else if (selectedClass !== 0) {
							return classStudentHashSet.get(selectedClass)?.has(user.id);
						}
					})
					.filter((user) => {
						if (search === '') {
							return true;
						} else {
							let name = user.name.toLowerCase();
							const query = search.toLowerCase();
							return name.includes(query);
						}
					})
					.sort(sortFactory(sortAttribute, ascending))
					.slice((page - 1) * 20, page * 20) as user}
					<tr class="bg-white border-b dark:bg-gray-900 dark:border-gray-700 text-xs">
						<td class="px-3 py-2 min-w-[7rem] w-28">
							<RoleSelector 
								items={$userRoles.map((role) => ({
									value: role.name,
									label: role.name
								}))}
								user={user}
								value={user.role}
								{updateRoleHandler}
							/>
						</td>
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

						<td class=" px-3 py-2">
							{dayjs(user.last_active_at * 1000).fromNow()}
						</td>

						<td class=" px-3 py-2">
							{dayjs(user.created_at * 1000).format($i18n.t('MMMM DD, YYYY'))}
						</td>

						<td class=" px-3 py-2">
							{userStatistics[user.id]?.token_count ?? 0}
						</td>

						<td class=" px-3 py-2">
							{userStatistics[user.id]?.attempts ?? 0}
						</td>

						<td class=" px-3 py-2">
							{approximateToHumanReadable((userStatistics[user.id]?.session_time ?? 0) * 1000000000)}
						</td>

						<td class="px-3 py-2 text-right w-32">
							<div class="flex justify-end w-full">
								<div class="flex justify-start min-w-24">
									<Tooltip content={$i18n.t('Chats')}>
										<button
										class="self-center w-fit text-sm px-2 py-2 hover:bg-black/5 dark:hover:bg-white/5 rounded-xl"
										on:click={async () => {
											showUserChatsModal = !showUserChatsModal;
											selectedUser = user;
										}}
											>
											<ChatBubbles />
										</button>
									</Tooltip>
									
									{#if user.role !== 'admin'}
										<Tooltip content={$i18n.t('Edit User')}>
											<button
												class="self-center w-fit text-sm px-2 py-2 hover:bg-black/5 dark:hover:bg-white/5 rounded-xl"
												on:click={async () => {
													showEditUserModal = !showEditUserModal;
													selectedUser = user;
												}}
											>
												<svg
													xmlns="http://www.w3.org/2000/svg"
													fill="none"
													viewBox="0 0 24 24"
													stroke-width="1.5"
													stroke="currentColor"
													class="w-4 h-4"
												>
													<path
														stroke-linecap="round"
														stroke-linejoin="round"
														d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L6.832 19.82a4.5 4.5 0 0 1-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 0 1 1.13-1.897L16.863 4.487Zm0 0L19.5 7.125"
													/>
												</svg>
											</button>
										</Tooltip>
	
										<Tooltip content={$i18n.t('Delete User')}>
											<button
												class="self-center w-fit text-sm px-2 py-2 hover:bg-black/5 dark:hover:bg-white/5 rounded-xl"
												on:click={async () => {
													showDeleteModal = !showDeleteModal;
													selectedUser = user;
												}}
											>
												<svg
													xmlns="http://www.w3.org/2000/svg"
													fill="none"
													viewBox="0 0 24 24"
													stroke-width="1.5"
													stroke="currentColor"
													class="w-4 h-4"
												>
													<path
														stroke-linecap="round"
														stroke-linejoin="round"
														d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0"
													/>
												</svg>
											</button>
										</Tooltip>
									{/if}
								</div>
							</div>
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>

	<div class=" text-gray-500 text-xs mt-2 text-left">
		ⓘ Click on the user role button to change a user's role. <br />
		ⓘ Statistics are estimates and do not include usage before tracking was enabled.  <br />
		ⓘ To enable tracking, go to Admin Panel > Models, select the model, check "Usage" under "Capabilities", and save the configuration.
	</div>

	<Pagination bind:page count={users.length} />
{/if}

<style>
	.font-mona {
		font-family: 'Mona Sans';
	}

	.scrollbar-hidden::-webkit-scrollbar {
		display: none; /* for Chrome, Safari and Opera */
	}

	.scrollbar-hidden {
		-ms-overflow-style: none; /* IE and Edge */
		scrollbar-width: none; /* Firefox */
	}
</style>
