<script lang="ts">
	import Modal from '../common/Modal.svelte';
    import SortableHeader from './SortableHeader.svelte';
    import { WEBUI_BASE_URL } from '$lib/constants';
    import i18n from '$lib/i18n';
	import dayjs from 'dayjs';
	import relativeTime from 'dayjs/plugin/relativeTime';
	dayjs.extend(relativeTime);

	export let show: boolean;
    export let deleteIds: Set<string>;
    export let users: any[];
    export let deleteHandler;

    const getRoleColor = (role: string) => {
        if (role === "admin") {
            return "sky";
        }
        if (role === "pending") {
            return "gray";
        }
        if (role === "user") {
            return "green";
        }

        // Adapted from https://stackoverflow.com/questions/7616461/generate-a-hash-from-string-in-javascript
        let hash = 0;
        for (let i = 0; i < role.length; i++) {
            let chr = role.charCodeAt(i);
            hash = ((hash << 5) - hash) + chr;
            hash |= 0; // Convert to 32bit integer
        }
        hash = Math.max(hash, -hash);
        
        const colorList = ["red", "orange", "amber", "yellow", "lime", "green", "emerald", "teal",
            "cyan", "sky", "blue", "indigo", "violet", "purple", "fuchsia", "pink", "rose"];
        return colorList[hash % colorList.length];
    }

    const buttonColors = {
        "gray":      "text-gray-600 dark:text-gray-200 bg-gray-200/30",
        "red":       "text-red-600 dark:text-red-200 bg-red-200/30",
        "orange":    "text-orange-600 dark:text-orange-200 bg-orange-200/30",
        "amber":     "text-amber-600 dark:text-amber-200 bg-amber-200/30",
        "yellow":    "text-yellow-600 dark:text-yellow-200 bg-yellow-200/30",
        "lime":      "text-lime-600 dark:text-lime-200 bg-lime-200/30",
        "green":     "text-green-600 dark:text-green-200 bg-green-200/30",
        "emerald":   "text-emerald-600 dark:text-emerald-200 bg-emerald-200/30",
        "teal":      "text-teal-600 dark:text-teal-200 bg-teal-200/30",
        "cyan":      "text-cyan-600 dark:text-cyan-200 bg-cyan-200/30",
        "sky":       "text-sky-600 dark:text-sky-200 bg-sky-200/30",
        "blue":      "text-blue-600 dark:text-blue-200 bg-blue-200/30",
        "indigo":    "text-indigo-600 dark:text-indigo-200 bg-indigo-200/30",
        "violet":    "text-violet-600 dark:text-violet-200 bg-violet-200/30",
        "purple":    "text-purple-600 dark:text-purple-200 bg-purple-200/30",
        "fuchsia":   "text-fuchsia-600 dark:text-fuchsia-200 bg-fuchsia-200/30",
        "pink":      "text-pink-600 dark:text-pink-200 bg-pink-200/30",
        "rose":      "text-rose-600 dark:text-rose-200 bg-rose-200/30",
    }

    const divColors = {
        "gray":     "bg-gray-600 dark:bg-gray-300",
        "red":      "bg-red-600 dark:bg-red-300",
        "orange":   "bg-orange-600 dark:bg-orange-300",
        "amber":    "bg-amber-600 dark:bg-amber-300",
        "yellow":   "bg-yellow-600 dark:bg-yellow-300",
        "lime":     "bg-lime-600 dark:bg-lime-300",
        "green":    "bg-green-600 dark:bg-green-300",
        "emerald":  "bg-emerald-600 dark:bg-emerald-300",
        "teal":     "bg-teal-600 dark:bg-teal-300",
        "cyan":     "bg-cyan-600 dark:bg-cyan-300",
        "sky":      "bg-sky-600 dark:bg-sky-300",
        "blue":     "bg-blue-600 dark:bg-blue-300",
        "indigo":   "bg-indigo-600 dark:bg-indigo-300",
        "violet":   "bg-violet-600 dark:bg-violet-300",
        "purple":   "bg-purple-600 dark:bg-purple-300",
        "fuchsia":  "bg-fuchsia-600 dark:bg-fuchsia-300",
        "pink":     "bg-pink-600 dark:bg-pink-300",
        "rose":     "bg-rose-600 dark:bg-rose-300",
    }

	let sortAttribute = "role";
	let ascending = true;
</script>

<Modal bind:show size="md">
	<div class="text-gray-700 dark:text-gray-100">
		<div class=" flex justify-between dark:text-gray-300 px-5 pt-4">
			<div class=" text-lg font-medium self-center">Confirm Deletion</div>
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
		
		<div class="flex flex-col pb-2 px-5">
			<div class="self-center text-sm font-normal mr-auto mb-2">
                Are you sure you want to delete the following users?<br>
                <strong>All chats of these users will also be deleted.</strong>
            </div>
            <div class="h-96">
                <div class="flex flex-col w-full h-full border border-gray-200 dark:border-gray-800 rounded-lg">
                    <div class="flex flex-row w-full gap-2 text-xs text-left text-gray-600 dark:text-gray-500 p-2">
                        <div class="w-1/6">{$i18n.t('Role')}</div>
                        <div class="w-1/3">{$i18n.t('Name')}</div>
                        <div class="w-1/3">{$i18n.t('Email')}</div>
                        <div class="w-1/6">{$i18n.t('Last Active')}</div>
                    </div>
                    <hr class="dark:border-gray-800" />
                    <div class="flex flex-col gap-2 space-y-1 overflow-scroll p-2">
                        {#each users.filter((user) => {
                            return deleteIds.has(user.id);
                        }) as user}
                            <div class="flex flex-row gap-2 w-full text-xs items-center">
                                <div class="flex w-1/6">
                                    <div class=" flex items-center gap-2 text-xs px-3 py-0.5 rounded-lg {`${buttonColors[getRoleColor(user.role)]}`}" >
                                        <div class="w-1 h-1 rounded-full {`${divColors[getRoleColor(user.role)]}`}" />
                                        {user.role}
                                    </div>
                                </div>
                                <div class="flex flex-row w-1/3">
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
                                <div class="w-1/3"> {user.email} </div>
                                <div class="w-1/6">
                                    {dayjs(user.last_active_at * 1000).fromNow()}
                                </div>
                            </div>
                        {/each}
                    </div>
                </div>
            </div>
		<div class="flex flex-row-reverse py-4">
			<button class="px-4 py-2 bg-red-200 hover:bg-red-300 dark:hover:bg-red-700 dark:bg-red-800 dark:text-gray-100 text-gray-900 transition rounded-lg"
				on:click={() => {
                    console.log("Deleting", deleteIds); 
                    deleteHandler(deleteIds);
                }}>
				Delete
			</button>
		</div>
	</div>
</Modal>

