<script lang="ts">
	import dayjs from 'dayjs';
	import { getContext, createEventDispatcher } from 'svelte';

	import Modal from '$lib/components/common/Modal.svelte';
	import { approximateToHumanReadable } from '$lib/utils';
	import SortableHeader from './SortableHeader.svelte';
    import { type ChatMetrics } from '$lib/apis/metrics'
    import { sortFactory } from '$lib/utils/index'

	const i18n = getContext('i18n');

	export let show = false;
	export let user_name = "";
	export let class_name = "";
	export let profile_name = "";

	export let chats = [];
    export let metrics: {
        [key: string]: ChatMetrics
    } = {};

	let sortAttribute = "updated_at";
	let ascending = false;
</script>

<Modal size="lg" bind:show>
	<div>
		<div class=" flex justify-between dark:text-gray-300 px-5 py-4">
			<div class=" text-lg font-medium self-center capitalize">
				{user_name}'s Attempts for {class_name} {profile_name}
			</div>
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
		<hr class=" dark:border-gray-850" />

		<div class="flex flex-col md:flex-row w-full px-5 py-4 md:space-x-4 dark:text-gray-200">
			<div class=" flex flex-col w-full sm:flex-row sm:justify-center sm:space-x-6">
				{#if chats?.length > 0}
					<div class="text-left text-sm w-full mb-4 max-h-[22rem] overflow-y-scroll">
						<div class="relative overflow-x-auto">
							<table class="w-full text-sm text-left text-gray-600 dark:text-gray-400 table-auto">
								<thead
									class="text-xs text-gray-700 uppercase bg-transparent dark:text-gray-200 border-b-2 dark:border-gray-800"
								>
									<tr>
										<th scope="col" class="px-3 py-2 min-w-1/3">
											<SortableHeader displayName={$i18n.t('Name')} attributeName="title"
												bind:currentAttribute={sortAttribute} bind:currentAscending={ascending}/>
										</th>
										<th scope="col" class="px-3 py-2 hidden md:table-cell">
											<SortableHeader displayName={$i18n.t('Updated at')} attributeName="updated_at"
												bind:currentAttribute={sortAttribute} bind:currentAscending={ascending}/>
										</th>
										<th scope="col" class="px-3 py-2 hidden md:table-cell">
											<SortableHeader displayName="Tokens Used" attributeName="token_count"
												bind:currentAttribute={sortAttribute} bind:currentAscending={ascending}/>
										</th>
										<th scope="col" class="px-3 py-2 hidden md:table-cell">
											<SortableHeader displayName="Chat Visits" attributeName="visits"
												bind:currentAttribute={sortAttribute} bind:currentAscending={ascending}/>
										</th>
										<th scope="col" class="px-3 py-2 hidden md:table-cell">
											<SortableHeader displayName="Session Time" attributeName="session_time"
												bind:currentAttribute={sortAttribute} bind:currentAscending={ascending}/>
										</th>
									</tr>
								</thead>
								<tbody>
									{#each chats.sort(sortFactory(sortAttribute, ascending)) as chat, idx}
										<tr
											class="{idx !== chats.length - 1 &&
												'border-b'} dark:border-gray-850 text-xs 
												{chat.is_submitted ? "bg-green-400/50 dark:bg-green-900/50" : "dark:bg-gray-900"}"
										>
											<td class="px-3 py-1 min-w-1/3">
												<a href="/s/{chat.id}" target="_blank">
													<div class=" underline line-clamp-1">
														{chat.title + (chat.is_submitted ? " (Submitted)" : "")}
													</div>
												</a>
											</td>

											<td class=" px-3 py-1 hidden md:table-cell h-[2.5rem]">
												<div class="my-auto">
													{dayjs(chat.updated_at * 1000).format($i18n.t('MMMM DD, YYYY HH:mm'))}
													({chat.time_range})
												</div>
											</td>

											<td class=" px-3 py-1 hidden md:table-cell h-[2.5rem]">
												<div class="my-auto">
													{metrics[chat.id] ? metrics[chat.id]?.input_tokens + metrics[chat.id]?.output_tokens : "No record"}
												</div>
											</td>

											<td class=" px-3 py-1 hidden md:table-cell h-[2.5rem]">
												<div class="my-auto">
													{chat.visits}
												</div>
											</td>

											<td class=" px-3 py-1 hidden md:table-cell h-[2.5rem]">
												<div class="my-auto">
													{approximateToHumanReadable(chat.session_time * 1000000000)}
												</div>
											</td>
										</tr>
									{/each}
								</tbody>
							</table>
						</div>
					</div>
				{:else}
					<div class="text-left text-sm w-full mb-8">
						{user_name}
						{$i18n.t('has no conversations.')}
					</div>
				{/if}
			</div>
		</div>
	</div>
</Modal>
