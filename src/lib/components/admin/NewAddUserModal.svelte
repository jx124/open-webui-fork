<script lang="ts">
	import { toast } from 'svelte-sonner';
	import { createEventDispatcher } from 'svelte';
	import { onMount, getContext } from 'svelte';

	import Modal from '../common/Modal.svelte';
	import { getRoles, updateUserRoles, type RoleForm } from '$lib/apis/roles';
	import { importUsers } from '$lib/apis/auths';
	import { userRoles } from '$lib/stores';
	import XMark from '../icons/XMark.svelte';
	import Share from '../icons/Share.svelte';
	import Check from '../icons/Check.svelte';
	import ChevronRight from '../icons/ChevronRight.svelte';
	import ChevronLeft from '../icons/ChevronLeft.svelte';
	import Plus from '../icons/Plus.svelte';

	const i18n = getContext('i18n');
	const dispatch = createEventDispatcher();

	export let show = false;
    export let users;
    export let inClass = false;
    export let selectedUsers;

	let loading = false;
	let tab = "list";

	let validRoles: Set<string>;

    type Entry = {
        name: string;
        email: string;
        role: string;
        invite: boolean;
    };

    function isEntryEmpty(entry: Entry) {
        return entry.name === "" && entry.email === "";
    }

    let entries: Entry[] = [{ name: "", email: "", role: "user", invite: false }];

    $: if (tab === "list" && !isEntryEmpty(entries.at(-1))) {
        entries.push({ name: "", email: "", role: "user", invite: false});
    }

    $: if (!show) {
        entries = [{ name: "", email: "", role: "user", invite: false }];
        tab = "list";
    }
    
    let newRoles: RoleForm[] = []

    let userEmailRoles: {
        [key: string]: string
    } = {};

    $: if (users) {
        for (const user of users) {
            userEmailRoles[user.email] = user.role;
        }
    }

    function pasteHandler(event: Event, index: number) {
        const text = event.clipboardData.getData("text/plain");
        const lines = text.split("\n");
        const results: Entry[] = []

        for (const line of lines) {
            const tokens: string[] = line.split("\t")
            if (tokens.length < 2) {
                return false;
            }
            if (tokens.length === 2) {
                results.push({ name: tokens[0].trim(), email: tokens[1].trim(), role: "user", invite: false});
            } else {
                const role = tokens[2].trim();
                if (!validRoles.has(role)) {
                    const newRole: RoleForm = { id: 0, name: role };
                    $userRoles = [...$userRoles, newRole];
                    validRoles.add(role);
                    newRoles.push(newRole);
                }
                results.push({ name: tokens[0].trim(), email: tokens[1].trim(), role: role, invite: false });
            }
        }

        if (!isEntryEmpty(entries[index])) {
            entries = [
                ...entries.slice(0, index + 1),
                ...results,
                ...entries.slice(index + 1)
            ];
        } else {
            entries = [
                ...entries.slice(0, index),
                ...results,
                ...entries.slice(index)
            ];
        }

        // prevent original text from being pasted
        event.preventDefault();
        return false;
    }

    function checkUsersHandler(event: Event) {
        let duplicateEmailEntries = [];
        let allEmails = new Set<string>();
        let invalid = false;

        for (const [index, entry] of entries.entries()) {
            if (index === entries.length - 1) {
                continue;
            }
            if (entry.name === "") {
                invalid = true;
                document.getElementById(`name-entry-${index}`).setCustomValidity("invalid");
            } else {
                document.getElementById(`name-entry-${index}`).setCustomValidity("");
            }

            if (entry.email === "") {
                invalid = true;
                document.getElementById(`email-entry-${index}`).setCustomValidity("invalid");
            } else {
                document.getElementById(`email-entry-${index}`).setCustomValidity("");
            }

            if (allEmails.has(entry.email)) {
                duplicateEmailEntries.push(index);
            } else {
                allEmails.add(entry.email);
            }
        }

        for (const index of duplicateEmailEntries) {
            invalid = true;
            document.getElementById(`email-entry-${index}`).setCustomValidity("invalid");
        }

        if (invalid) {
            toast.error("Invalid entry. Please ensure names are filled in and there are no duplicate emails.");
            return;
        }
        entries.splice(entries.length - 1, 1);

        for (const [index, entry] of entries.entries()) {
            if (!userEmailRoles[entry.email]) {
                entries[index].invite = true;
            }
        }

        tab = "check";
    }

    async function submitHandler() {
        loading = true;
        let error = false;
        let invitedRoles = new Set<string>();
        let invitedUsers = [];

        for (const entry of entries) {
            if (entry.invite) {
                invitedRoles.add(entry.role);
                invitedUsers.push({ name: entry.name, email: entry.email, role: entry.role });
            }
        }

        let newInvitedRoles: RoleForm[] = [];
        for (const role of newRoles) {
            if (invitedRoles.has(role.name)) {
                newInvitedRoles.push(role);
            }
        }

        if (newInvitedRoles.length > 0) {
            await updateUserRoles(localStorage.token, newInvitedRoles)
                .then((res) => $userRoles = res)
                .catch((err) => {
                    toast.error(err);
                    error = true;
                });

            if (error) {
                loading = false;
                return ;
            }
        }
        
        if (invitedUsers.length > 0) {
            await importUsers(localStorage.token, invitedUsers)
                .then((res) => users = res)
                .catch((err) => {
                    toast.error(err);
                    error = true;
                });

            if (error) {
                loading = false;
                return ;
            }
        }

        if (inClass) {
            // we need to add to existing selectedUsers and deduplicate
            let entriesEmailSet = new Set(entries.map(user => user.email));
            let newSelectedUsers = users.filter(user => entriesEmailSet.has(user.email)).map(user => user.id);
            selectedUsers = Array.from(new Set([...selectedUsers, ...newSelectedUsers]));
        }

		dispatch('save');
        loading = false;
    }

	onMount(async () => {
		$userRoles = await getRoles(localStorage.token);
		validRoles = new Set($userRoles.map(role => role.name));
	})
</script>

<Modal size="md" bind:show>
	<div class="">
		<div class="flex justify-between dark:text-gray-300 px-5 pt-4 pb-2">
			<div class=" text-lg font-medium self-center">{$i18n.t('Add User')}</div>
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

		<div class="flex flex-col md:flex-row w-full px-5 pb-4 md:space-x-4 dark:text-gray-200">
			<div class=" flex flex-col w-full sm:flex-row sm:justify-center sm:space-x-6">
				<form
					class="flex flex-col w-full"
					on:submit|preventDefault={async () => {
                        await submitHandler();
                        tab = "invite";
					}}
				>
					<div class="flex text-center items-center justify-between text-sm font-medium rounded-xl p-1 mb-2 mx-4">
                        <div class="flex flex-col items-center">
                            <div
                                class="flex rounded-full w-9 h-9 items-center justify-center {tab === 'list' ? 'bg-gray-900 text-white dark:bg-gray-100 dark:text-gray-900' : 'bg-gray-100 dark:bg-gray-800'}"
                            >
                                1
                            </div>
                            <div class="mt-2"> List </div>
                        </div>
                        <hr class="flex flex-grow self-start border-gray-200 dark:border-gray-800 mx-2 mt-4"/>

                        <div class="flex flex-col items-center">
                            <div
                                class="flex rounded-full w-9 h-9 items-center justify-center {tab === 'check' ? 'bg-gray-900 text-white dark:bg-gray-100 dark:text-gray-900' : 'bg-gray-100 dark:bg-gray-800'}"
                            >
                                2
                            </div>
                            <div class="mt-2"> Check </div>
                        </div>
                        <hr class="flex flex-grow self-start border-gray-200 dark:border-gray-800 mx-2 mt-4"/>

                        <div class="flex flex-col items-center">
                            <div
                                class="flex rounded-full w-9 h-9 items-center justify-center {tab === 'invite' ? 'bg-gray-900 text-white dark:bg-gray-100 dark:text-gray-900' : 'bg-gray-100 dark:bg-gray-800'}"
                            >
                                3
                            </div>
                            <div class="mt-2"> Invite </div>
                        </div>
					</div>
					<div class="px-1 h-96">
						{#if tab === "list"}
                            <div class="flex flex-col w-full h-full border border-gray-200 dark:border-gray-800 rounded-lg">
                                <div class="flex flex-row w-full gap-2 text-xs text-gray-600 dark:text-gray-500 p-2">
                                    <div class="w-6" />
                                    <div class="w-2/5">{$i18n.t('Name')}</div>
                                    <div class="w-2/5">{$i18n.t('Email')}</div>
                                    <div class="w-1/5">{$i18n.t('Role')}</div>
                                    <div class="w-4" />
                                </div>
                                <hr class="dark:border-gray-800" />
                                <div class="flex flex-col gap-2 overflow-scroll p-2">
                                    {#each entries as entry, index}
                                        <div class="flex flex-row gap-2 w-full">
                                            <div class="flex items-center w-6 text-sm dark:text-gray-500">
                                                {index + 1}
                                            </div>
                                            <input
                                                class="w-2/5 rounded-lg py-2 px-4 text-sm border border-gray-200 dark:border-none dark:text-gray-300 dark:bg-gray-850 disabled:text-gray-500 dark:disabled:text-gray-500 invalid:border-red-500 invalid:text-red-500"
                                                type="text"
                                                id="name-entry-{index}"
                                                bind:value={entries[index].name}
                                                on:paste={(event) => pasteHandler(event, index)}
                                                autocomplete="off"
                                            />
                                            <input
                                                class="w-2/5 rounded-lg py-2 px-4 text-sm border border-gray-200 dark:border-none dark:text-gray-300 dark:bg-gray-850 disabled:text-gray-500 dark:disabled:text-gray-500 invalid:border-red-500 invalid:text-red-500"
                                                type="email"
                                                id="email-entry-{index}"
                                                bind:value={entries[index].email}
                                                on:paste={(event) => pasteHandler(event, index)}
                                                autocomplete="off"
                                            />
                                            <select
                                                class="w-1/5 rounded-lg py-2 px-4 text-sm dark:text-gray-300 dark:bg-gray-850 disabled:text-gray-500 dark:disabled:text-gray-500"
                                                bind:value={entries[index].role}
                                                required
                                            >
                                                {#each $userRoles as role}
                                                    <option value={role.name}> {role.name} </option>
                                                {/each}
                                            </select>
                                            {#if !isEntryEmpty(entry)}
                                                <button class="flex items-center w-4 text-sm hover:text-gray-800 dark:hover:text-gray-100 dark:text-gray-400 text-gray-500"
                                                    type="button"
                                                    on:click|preventDefault={() => {
                                                        entries.splice(index, 1);
                                                        entries = entries;
                                                    }}>
                                                        <XMark />
                                                </button>
                                            {:else}
                                                <div class="w-4" />
                                            {/if}
                                        </div>
                                    {/each}
                                </div>
							</div>
                        {:else}
                            <div class="flex flex-col w-full h-full border border-gray-200 dark:border-gray-800 rounded-lg">
                                <div class="flex flex-row w-full gap-2 text-xs text-gray-600 dark:text-gray-500 p-2">
                                    <div class="w-6" />
                                    <div class="w-1/3">{$i18n.t('Name')}</div>
                                    <div class="w-1/3">{$i18n.t('Email')}</div>
                                    <div class="w-1/3 flex flex-row">
                                        <div class="w-1/3">
                                            {$i18n.t('Role')}
                                        </div>
                                        <div class="w-2/3">
                                            Action
                                        </div>
                                    </div>
                                </div>
                                <hr class="dark:border-gray-800" />
                                <div class="flex flex-col gap-2 overflow-scroll p-2">
                                    {#each entries as entry, index}
                                        <div class="flex flex-row gap-2 w-full">
                                            <div class="flex items-center w-6 text-sm dark:text-gray-500">
                                                {index + 1}
                                            </div>
                                            <div class="flex items-center w-1/3 text-sm dark:text-gray-500">
                                                {entry.name}
                                            </div>
                                            <div class="flex items-center w-1/3 text-sm dark:text-gray-500">
                                                {entry.email}
                                            </div>
                                            <div class="flex items-center w-1/3 text-sm dark:text-gray-500">
                                                <div class="w-1/3">
                                                    {entry.role}
                                                </div>
                                                {#if entry.invite}
                                                    <div class="w-2/3 flex gap-1 items-center text-xs font-semibold text-purple-500 dark:text-purple-400">
                                                        {#if inClass}
                                                            <Share /> Invite to class
                                                        {:else}
                                                            <Share /> Send Invitation
                                                        {/if}
                                                    </div>
                                                {:else if inClass}
                                                    <div class="w-2/3 flex gap-1 items-center text-xs font-semibold text-green-600 dark:text-green-400">
                                                        <Plus /> Add to class
                                                    </div>
                                                {:else}
                                                    <div class="w-2/3 flex gap-1 items-center text-xs font-semibold text-black dark:text-white">
                                                        <Check /> Existing {userEmailRoles[entry.email]}
                                                    </div>
                                                {/if}
                                            </div>
                                        </div>
                                    {/each}
                                </div>
							</div>
						{/if}
					</div>

					<div class="flex justify-between pt-3 text-sm font-medium">
                        {#if tab === "list"}
                            <div class=" text-gray-600 dark:text-gray-500 align-start text-xs text-left">
                                ⓘ To <strong>bulk import</strong>, directly paste values in from a spreadsheet. Ensure that at least the name and email columns are present.
                            </div>
                            <button
                                class="gap-1 px-4 py-2 bg-gray-200 hover:bg-gray-300 dark:hover:bg-gray-700 dark:bg-gray-800 dark:text-gray-100 text-gray-900 transition rounded-lg flex flex-row space-x-1 items-center whitespace-nowrap disabled:hover:bg-gray-200 disabled:dark:hover:bg-gray-800 disabled:cursor-not-allowed"
                                type="button"
                                on:click={checkUsersHandler}
                                disabled={entries.length === 1}
                            >
                                Check Users <ChevronRight />
                            </button>
                        {:else if tab === "check"}
                            <button
                                class="gap-1 px-4 py-2 bg-gray-200 hover:bg-gray-300 dark:hover:bg-gray-700 dark:bg-gray-800 dark:text-gray-100 text-gray-900 transition rounded-lg flex flex-row space-x-1 items-center disabled:hover:bg-gray-200 disabled:dark:hover:bg-gray-800 disabled:cursor-not-allowed"
                                type="button"
                                on:click={() => {tab = "list";}}
                            >
                                <ChevronLeft /> Edit Invites
                            </button>
                            <button
                                class="gap-1 px-4 py-2 bg-gray-200 hover:bg-gray-300 dark:hover:bg-gray-700 dark:bg-gray-800 dark:text-gray-100 text-gray-900 transition rounded-lg flex flex-row space-x-1 items-center {loading
                                    ? ' cursor-not-allowed'
                                    : ''}"
                                type="submit"
                                disabled={loading}
                            >
                                Apply Actions <ChevronRight />
                                {#if loading}
                                    <div class="ml-2 self-center">
                                        <svg
                                            class=" w-4 h-4"
                                            viewBox="0 0 24 24"
                                            fill="currentColor"
                                            xmlns="http://www.w3.org/2000/svg"
                                            ><style>
                                                .spinner_ajPY {
                                                    transform-origin: center;
                                                    animation: spinner_AtaB 0.75s infinite linear;
                                                }
                                                @keyframes spinner_AtaB {
                                                    100% {
                                                        transform: rotate(360deg);
                                                    }
                                                }
                                            </style><path
                                                d="M12,1A11,11,0,1,0,23,12,11,11,0,0,0,12,1Zm0,19a8,8,0,1,1,8-8A8,8,0,0,1,12,20Z"
                                                opacity=".25"
                                            /><path
                                                d="M10.14,1.16a11,11,0,0,0-9,8.92A1.59,1.59,0,0,0,2.46,12,1.52,1.52,0,0,0,4.11,10.7a8,8,0,0,1,6.66-6.61A1.42,1.42,0,0,0,12,2.69h0A1.57,1.57,0,0,0,10.14,1.16Z"
                                                class="spinner_ajPY"
                                            /></svg
                                        >
                                    </div>
                                {/if}
                            </button>
                        {:else}
                            <div />
                            <button
                                class="gap-1 px-4 py-2 bg-gray-200 hover:bg-gray-300 dark:hover:bg-gray-700 dark:bg-gray-800 dark:text-gray-100 text-gray-900 transition rounded-lg flex flex-row space-x-1 items-center"
                                type="button"
                                on:click={() => {show = false;}}
                            >
                                Done
                            </button>
                        {/if}
					</div>
				</form>
			</div>
		</div>
	</div>
</Modal>

<style>
	input::-webkit-outer-spin-button,
	input::-webkit-inner-spin-button {
		/* display: none; <- Crashes Chrome on hover */
		-webkit-appearance: none;
		margin: 0; /* <-- Apparently some margin are still there even though it's hidden */
	}

	.tabs::-webkit-scrollbar {
		display: none; /* for Chrome, Safari and Opera */
	}

	.tabs {
		-ms-overflow-style: none; /* IE and Edge */
		scrollbar-width: none; /* Firefox */
	}

	input[type='number'] {
		-moz-appearance: textfield; /* Firefox */
	}
</style>

