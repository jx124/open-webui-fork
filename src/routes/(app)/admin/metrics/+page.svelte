<script lang="ts">
	import { toast } from 'svelte-sonner';
	import { getMetrics, type Metrics } from "$lib/apis/metrics";
	import { getAllUserChatsAbridged } from "$lib/apis/chats";
	import ClassSearchbar from "$lib/components/admin/ClassSearchbar.svelte";
	import PlainDropdown from "$lib/components/admin/PlainDropdown.svelte";
	import ProfileSearchbar from "$lib/components/admin/ProfileSearchbar.svelte";
	import { classes, prompts, WEBUI_NAME } from "$lib/stores";
	import { WEBUI_BASE_URL } from "$lib/constants";
	import { onMount } from "svelte";
	import SortableHeader from '$lib/components/admin/SortableHeader.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import ChatBubbles from '$lib/components/icons/ChatBubbles.svelte';
	import Pagination from '$lib/components/common/Pagination.svelte';
	import { getUserProfiles } from '$lib/apis/users';
	import { getPromptTitles } from '$lib/apis/prompts';
	import DatePicker from '$lib/components/common/DatePicker.svelte';
    import { sortFactory } from '$lib/utils/index'

    let loaded = false;

    let metrics: Metrics[];
    let filteredMetrics: Metrics[];

    let startDate = new Date();
    let endDate = new Date();
    const now = new Date();

    let chats = {};
    let chatDetailsMap: {
        [key: string]: {
            class_id: number,
            prompt_id: number,
            title: string,
        }
    } = {};

    let totalInputTokens = 0;
    let totalOutputTokens = 0;
    let totalMessageCount = 0
    let totalCost = 0;

    // TODO: include caching
    const modelPricesPerMTokens: {
        [key: string]: { input: number, output: number }
    } = {
        "gpt-4.1": { input: 2.00, output: 8.00 },
        "gpt-4.1-mini": { input: 0.40, output: 1.60 },
        "gpt-4.1-nano": { input: 0.10, output: 0.40 },
        "gpt-4.5-preview": { input: 75.00, output: 150.00 },
        "gpt-4o": { input: 2.50, output: 10.00 },
        "gpt-4o-audio-preview": { input: 2.50, output: 10.00 },
        "gpt-4o-realtime-preview": { input: 5.00, output: 20.00 },
        "gpt-4o-mini": { input: 0.15, output: 0.60 },
        "gpt-4o-mini-audio-preview": { input: 0.15, output: 0.60 },
        "gpt-4o-mini-realtime-preview": { input: 0.60, output: 2.40 },
        "o1": { input: 15.00, output: 60.00 },
        "o1-pro": { input: 150.00, output: 600.00 },
        "o3-pro": { input: 20.00, output: 80.00 },
        "o3": { input: 2.00, output: 8.00 },
        "o3-deep-research": { input: 10.00, output: 40.00 },
        "o4-mini": { input: 1.10, output: 4.40 },
        "o4-mini-deep-research": { input: 2.00, output: 8.00 },
        "o3-mini": { input: 1.10, output: 4.40 },
        "o1-mini": { input: 1.10, output: 4.40 },
        "codex-mini-latest": { input: 1.50, output: 6.00 },
        "gpt-4o-mini-search-preview": { input: 0.15, output: 0.60 },
        "gpt-4o-search-preview": { input: 2.50, output: 10.00 },
        "computer-use-preview": { input: 3.00, output: 12.00 },
        "gpt-image-1": { input: 5.00, output: 0 },
        "claude-2.0": { input: 8, output: 24 },
        "claude-2.1": { input: 8, output: 24 },
        "claude-3-haiku-20240307": { input: 0.25, output: 1.25 },
        "claude-3-5-haiku-20241022": { input: 0.80, output: 4 },
        "claude-3-opus-20240229": { input: 15, output: 75 },
        "claude-opus-4-20250514": { input: 15, output: 75 },
        "claude-3-sonnet-20240229": { input: 3, output: 15 },
        "claude-3-5-sonnet-20241022": { input: 3, output: 15 },
        "claude-3-5-sonnet-20240620": { input: 3, output: 15 },
        "claude-3-7-sonnet-20250219": { input: 3, output: 15 },
        "claude-sonnet-4-20250514": { input: 3, output: 15 },
    }

    $: if (metrics) {
        // include actual end date by adding extra day
        let actualEndDate = new Date(endDate);
        actualEndDate.setDate(actualEndDate.getDate() + 1);

        filteredMetrics = metrics.filter(metric => { // date filter
            // TODO: use an enum
            if (selectedDateId === 0) {
                // current month
                return metric.date.getMonth() === now.getMonth() && metric.date.getFullYear() === now.getFullYear()
            } else if (selectedDateId === 1) {
                // all
                return true;
            } else if (selectedDateId === 2) {
                return startDate <= metric.date && metric.date < actualEndDate; 
            }
        }).filter(metric => {
            if (selectedClassId === 0) {
                return true;
            } else {
                return chatDetailsMap[metric.chat_id].class_id === selectedClassId;
            }
        }).filter(metric => {
            if (selectedProfileId === 0) {
                return true;
            } else {
                return chatDetailsMap[metric.chat_id].prompt_id === selectedProfileId;
            }
        })

        totalInputTokens = 0;
        totalOutputTokens = 0;
        totalMessageCount = 0
        totalCost = 0;

        for (const metric of filteredMetrics) {
            totalInputTokens += metric.input_tokens;
            totalOutputTokens += metric.output_tokens;
            totalMessageCount += metric.message_count;
            totalCost += (modelPricesPerMTokens[metric.selected_model_id]?.input ?? 0) * metric.input_tokens / 1000000;
            totalCost += (modelPricesPerMTokens[metric.selected_model_id]?.output ?? 0) * metric.output_tokens / 1000000;
        }
    }

    $: if (filteredMetrics) {
        let modelEntriesMap: {
            [key: string]: ModelEntry;
        } = {};

        let chatEntriesMap: {
            [key: string]: ChatEntry;
        } = {};

        for (const metric of filteredMetrics) {
            const cost = (modelPricesPerMTokens[metric.selected_model_id]?.input ?? 0) * metric.input_tokens / 1000000
                       + (modelPricesPerMTokens[metric.selected_model_id]?.output ?? 0) * metric.output_tokens / 1000000;

            if (modelEntriesMap.hasOwnProperty(metric.selected_model_id)) {
                let entry = modelEntriesMap[metric.selected_model_id];
                entry.input_tokens += metric.input_tokens;
                entry.output_tokens += metric.output_tokens;
                entry.total_tokens += metric.input_tokens + metric.output_tokens,
                entry.message_count += metric.message_count;
                entry.cost += cost;
            } else {
                modelEntriesMap[metric.selected_model_id] = {
                    selected_model_id: metric.selected_model_id,
                    input_tokens: metric.input_tokens,
                    output_tokens: metric.output_tokens,
                    total_tokens: metric.input_tokens + metric.output_tokens,
                    message_count: metric.message_count,
                    cost: cost
                };
            }

            if (chatEntriesMap.hasOwnProperty(metric.chat_id)) {
                let entry = chatEntriesMap[metric.chat_id];
                entry.input_tokens += metric.input_tokens;
                entry.output_tokens += metric.output_tokens;
                entry.total_tokens += metric.input_tokens + metric.output_tokens,
                entry.message_count += metric.message_count;
                entry.cost += cost;

            } else {
                const classId = chatDetailsMap[metric.chat_id]?.class_id ?? 0;
                const profileId = chatDetailsMap[metric.chat_id]?.prompt_id ?? 0;
                chatEntriesMap[metric.chat_id] = {
                    user_id: metric.user_id,
                    user_name: userProfiles[metric.user_id]?.name ?? "Deleted User",
                    profile_image_url: userProfiles[metric.user_id]?.profile_image_url ?? "/user.png",
                    class_id: classId,
                    class_name: classNameMap[classId] ?? "Deleted Class",
                    profile_id: profileId,
                    profile_title: profileTitles[profileId] ?? "Deleted Profile",
                    chat_id: metric.chat_id,
                    chat_title: chatDetailsMap[metric.chat_id]?.title ?? "Deleted Chat",
                    input_tokens: metric.input_tokens,
                    output_tokens: metric.output_tokens,
                    total_tokens: metric.input_tokens + metric.output_tokens,
                    message_count: metric.message_count,
                    cost: cost,
                };
            }
        }
        let tempModelArray: ModelEntry[] = [];
        for (const entry in modelEntriesMap) {
            tempModelArray.push(modelEntriesMap[entry]);
        }
        modelEntries = tempModelArray;

        let tempChatArray: ChatEntry[] = [];
        for (const entry in chatEntriesMap) {
            tempChatArray.push(chatEntriesMap[entry]);
        }
        chatEntries = tempChatArray;
    }

	let dateItems: {
		label: string;
		value: number;
	}[] = [
        { label: "Current Month", value: 0 },
        { label: "All", value: 1 },
        { label: "Custom Date Range", value: 2 },
    ]
	let selectedDateId = 0;

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
    let classNameMap: { [key: number]: string } = {};

	let modelSortAttribute = "selected_model_id";
	let modelAscending = true;

    let search = "";
	let chatSortAttribute = "user_name";
	let chatAscending = true;
    let page = 1;

    type ModelEntry = {
        selected_model_id: string;
        input_tokens: number;
        output_tokens: number;
        total_tokens: number;
        message_count: number;
        cost: number;
    }

    let modelEntries: ModelEntry[] = [];

    type ChatEntry = {
		user_id: string
        user_name: string;
        profile_image_url: string;
        class_id: number;
        class_name: string;
        profile_id: number;
		profile_title: string;
        chat_id: string;
        chat_title: string;
        input_tokens: number;
        output_tokens: number;
        total_tokens: number;
        message_count: number;
        cost: number;
    }

    let chatEntries: ChatEntry[] = [];
    let userProfiles: {
        [key: string]: {
            name: string;
            profile_image_url: string;
        }
    } = {};
    let profileTitles: {
        [key: number]: string;
   } = {};

    onMount(async () => {
        metrics = await getMetrics(localStorage.token)
            .then(res => {
                return res.map(metric => { return { ...metric, date: new Date(Date.parse(metric.date)) }})
            })
            .catch(err => toast.error(err));
        console.log("metrics", metrics);

        chats = await getAllUserChatsAbridged(localStorage.token);
        for (const chat of chats) {
            chatDetailsMap[chat.id] = {
                class_id: chat.class_id,
                prompt_id: chat.prompt_id,
                title: chat.title
            };
        }

        console.log("chats", chats);

		userProfiles = await getUserProfiles(localStorage.token);
        profileTitles = await getPromptTitles(localStorage.token);
        
        for (const class_ of $classes) {
			classAssignmentMap.set(class_.id, new Set<number>(class_.assignments.map(a => a.prompt_id)));
            classNameMap[class_.id] = class_.name;
        }

        console.log("classNameMap", classNameMap);
        console.log("profileTitles", profileTitles);

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
		Metrics | {$WEBUI_NAME}
	</title>
</svelte:head>

{#if loaded}
    <div class="flex flex-col">
        <div class="flex gap-4">
            <div class="flex flex-col">
                <div class="font-semibold text-sm mb-1">Date Filter</div>
                <PlainDropdown
                    items={dateItems}
                    bind:value={selectedDateId}
                />
            </div>
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
                    class=" text-sm px-3 py-1.5 transition rounded-xl bg-gray-200 hover:bg-gray-300 dark:hover:bg-gray-700 dark:bg-gray-800 dark:text-gray-100 text-gray-900 flex"
                    on:click={() => {
                        selectedClassId = 0;
                        selectedProfileId = 0;
                        selectedDateId = 0;
                    }}
                    type="button"
                >
                    <div class=" self-center font-medium">Reset</div>
                </button>
            </div>
        </div>
        {#if selectedDateId === 2}
            <div class="flex flex-row gap-2">
                <DatePicker label={"Start Date:"} bind:selectedDate={startDate} placeholder={now} />
                <DatePicker label={"End Date:"} bind:selectedDate={endDate} placeholder={now} />
            </div>
        {/if}
    </div>

    <div class="font-medium text-lg my-2">Overview</div>
    <div class="flex flex-row gap-2">
        <div class="p-4 mb-4 rounded-md border dark:border-gray-600"> 
            Total input tokens<br>
            <span class="font-bold text-2xl">{totalInputTokens}</span>
        </div>
        <div class="p-4 mb-4 rounded-md border dark:border-gray-600"> 
            Total output tokens<br>
            <span class="font-bold text-2xl">{totalOutputTokens}</span>
        </div>
        <div class="p-4 mb-4 rounded-md border dark:border-gray-600"> 
            Total tokens used<br>
            <span class="font-bold text-2xl">{totalInputTokens + totalOutputTokens}</span>
        </div>
        <div class="p-4 mb-4 rounded-md border dark:border-gray-600"> 
            User messages sent<br>
            <span class="font-bold text-2xl">{totalMessageCount}</span>
        </div>
        <div class="p-4 mb-4 rounded-md border dark:border-gray-600"> 
            Total chat sessions<br>
            <span class="font-bold text-2xl">{chatEntries.length}</span>
        </div>
        <div class="p-4 mb-4 rounded-md border dark:border-gray-600"> 
            Total estimated cost<br>
            <span class="font-bold text-2xl">${totalCost.toFixed(2)}</span>
        </div>
        <div class="p-4 mb-4 rounded-md border dark:border-gray-600"> 
            Average cost per session<br>
            <span class="font-bold text-2xl">${(totalCost / chatEntries.length).toFixed(2)}</span>
        </div>
    </div>

    <div class="font-medium text-lg my-2">Breakdown by Model</div>
	<div class="scrollbar-hidden relative whitespace-nowrap overflow-x-auto max-w-full">
		<table class="w-full text-sm text-left text-gray-600 dark:text-gray-400 table-auto max-w-full">
			<thead class="text-xs text-gray-700 uppercase bg-gray-100 dark:bg-gray-850 dark:text-gray-400">
				<tr>
					<th scope="col" class="px-3 py-2"> 
						<SortableHeader displayName="Model Name" attributeName="selected_model_id"
							bind:currentAttribute={modelSortAttribute} bind:currentAscending={modelAscending}/>
					</th>
					<th scope="col" class="px-3 py-2">
						<SortableHeader displayName="Input Tokens" attributeName="input_tokens"
							bind:currentAttribute={modelSortAttribute} bind:currentAscending={modelAscending}/>
					</th>
					<th scope="col" class="px-3 py-2">
						<SortableHeader displayName="Output Tokens" attributeName="output_tokens"
							bind:currentAttribute={modelSortAttribute} bind:currentAscending={modelAscending}/>
					</th>
					<th scope="col" class="px-3 py-2">
						<SortableHeader displayName="Total Tokens" attributeName="total_tokens"
							bind:currentAttribute={modelSortAttribute} bind:currentAscending={modelAscending}/>
					</th>
					<th scope="col" class="px-3 py-2">
						<SortableHeader displayName="User Messages Sent" attributeName="message_count"
							bind:currentAttribute={modelSortAttribute} bind:currentAscending={modelAscending}/>
					</th>
					<th scope="col" class="px-3 py-2">
						<SortableHeader displayName="Estimated Cost" attributeName="cost"
							bind:currentAttribute={modelSortAttribute} bind:currentAscending={modelAscending}/>
					</th>
				</tr>
			</thead>
			<tbody>
				{#each modelEntries.sort(sortFactory(modelSortAttribute, modelAscending)) as entry}
					<tr class="bg-white border-b dark:bg-gray-900 dark:border-gray-700 text-sm w-full">
						<td class="px-3 py-2"> {entry.selected_model_id} </td>
						<td class="px-3 py-2"> {entry.input_tokens} </td>
						<td class="px-3 py-2"> {entry.output_tokens} </td>
						<td class="px-3 py-2"> {entry.total_tokens} </td>
						<td class="px-3 py-2"> {entry.message_count} </td>
						<td class="px-3 py-2"> ${entry.cost.toFixed(7)} </td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>

    <div class="font-medium text-lg mb-2 mt-6">Breakdown by Chat</div>
	<div class="mb-2 scrollbar-hidden relative whitespace-nowrap overflow-x-auto max-w-full">
		<table class="w-full text-sm text-left text-gray-600 dark:text-gray-400 table-auto max-w-full">
			<thead class="text-xs text-gray-700 uppercase bg-gray-100 dark:bg-gray-850 dark:text-gray-400">
				<tr>
					<th scope="col" class="px-3 py-2"> 
						<SortableHeader displayName="Name" attributeName="user_name"
							bind:currentAttribute={chatSortAttribute} bind:currentAscending={chatAscending}/>
					</th>
					<th scope="col" class="px-3 py-2"> 
						<SortableHeader displayName="Class" attributeName="class_name"
							bind:currentAttribute={chatSortAttribute} bind:currentAscending={chatAscending}/>
					</th>
					<th scope="col" class="px-3 py-2"> 
						<SortableHeader displayName="Profile" attributeName="profile_title"
							bind:currentAttribute={chatSortAttribute} bind:currentAscending={chatAscending}/>
					</th>
					<th scope="col" class="px-3 py-2"> 
						<SortableHeader displayName="Chat" attributeName="chat_title"
							bind:currentAttribute={chatSortAttribute} bind:currentAscending={chatAscending}/>
					</th>
					<th scope="col" class="px-3 py-2">
						<SortableHeader displayName="Input Tokens" attributeName="input_tokens"
							bind:currentAttribute={chatSortAttribute} bind:currentAscending={chatAscending}/>
					</th>
					<th scope="col" class="px-3 py-2">
						<SortableHeader displayName="Output Tokens" attributeName="output_tokens"
							bind:currentAttribute={chatSortAttribute} bind:currentAscending={chatAscending}/>
					</th>
					<th scope="col" class="px-3 py-2">
						<SortableHeader displayName="Total Tokens" attributeName="total_tokens"
							bind:currentAttribute={chatSortAttribute} bind:currentAscending={chatAscending}/>
					</th>
					<th scope="col" class="px-3 py-2">
						<SortableHeader displayName="User Messages Sent" attributeName="message_count"
							bind:currentAttribute={chatSortAttribute} bind:currentAscending={chatAscending}/>
					</th>
					<th scope="col" class="px-3 py-2">
						<SortableHeader displayName="Estimated Cost" attributeName="cost"
							bind:currentAttribute={chatSortAttribute} bind:currentAscending={chatAscending}/>
					</th>
				</tr>
			</thead>
			<tbody>
				{#each chatEntries.sort(sortFactory(chatSortAttribute, chatAscending)) as entry}
					<tr class="bg-white border-b dark:bg-gray-900 dark:border-gray-700 text-sm w-full">
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
						<td class="px-3 py-2"> {entry.class_name} </td>
						<td class="px-3 py-2"> {entry.profile_title} </td>
						<td class="px-3 py-2">
                            <a href="/s/{entry.chat_id}" target="_blank">
                                <div class=" underline line-clamp-1">
                                    {entry.chat_title}
                                </div>
                            </a>
                        </td>
						<td class="px-3 py-2"> {entry.input_tokens} </td>
						<td class="px-3 py-2"> {entry.output_tokens} </td>
						<td class="px-3 py-2"> {entry.total_tokens} </td>
						<td class="px-3 py-2"> {entry.message_count} </td>
						<td class="px-3 py-2"> ${entry.cost.toFixed(7)} </td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>

	<div class="text-gray-600 dark:text-gray-500 text-xs mt-2 text-left">
		ⓘ Statistics are estimates and do not include usage before tracking was enabled.  <br />
	</div>
	<Pagination bind:page count={modelEntries.length} />
{/if}
