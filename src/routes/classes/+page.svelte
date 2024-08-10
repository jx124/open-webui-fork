<script lang="ts">
	import { classes, prompts, showArchivedChats, user, WEBUI_NAME } from '$lib/stores';
	import UserMenu from '$lib/components/layout/Sidebar/UserMenu.svelte';
	import { WEBUI_BASE_URL } from '$lib/constants';
	import { onMount } from 'svelte';
	import { getClassList } from '$lib/apis/classes';
	import { toast } from 'svelte-sonner';
	import { getPrompts } from '$lib/apis/prompts';

	let searchValue = '';
	let loading = true;

	const assignedPromptLabel = (prompt_ids: number[]) => {
		if (prompt_ids.length === 0) {
			return 'No assigned prompts';
		}
		return (
			'Assigned Prompts: ' +
			$prompts
				.filter((p) => prompt_ids.includes(p.id))
				.map((p) => p.title)
				.join(', ')
		);
	};

	onMount(async () => {
		if ($classes.length === 0) {
			$classes = await getClassList(localStorage.token).catch((error) => toast.error(error));
		}
		if ($prompts.length === 0) {
			$prompts = await getPrompts(localStorage.token).catch((error) => toast.error(error));
		}
		loading = false;
	});
</script>

<svelte:head>
	<title>
		Classes | {$WEBUI_NAME}
	</title>
</svelte:head>

<div class="app relative">
	<div
		class=" text-gray-700 dark:text-gray-100 bg-white dark:bg-gray-900 min-h-screen overflow-auto flex flex-row"
	>
		<div class="min-h-[calc(100dvh)] max-h-[calc(100dvh)] w-full max-w-full flex flex-col">
			<nav id="nav" class=" sticky py-2.5 top-0 flex flex-row justify-center z-30">
				<div
					class="px-2.5 flex items-center justify-between w-full max-w-full text-gray-600 dark:text-gray-400"
				>
					<div class="flex justify-between space-x-1 text-gray-600 dark:text-gray-400">
						<a
							id="sidebar-new-chat-button"
							class="flex flex-1 justify-between rounded-xl px-2 py-2 hover:bg-gray-100 dark:hover:bg-gray-850 transition"
							href="/"
							draggable="false"
						>
							<div class="self-center mx-1.5">
								<img
									crossorigin="anonymous"
									src="{WEBUI_BASE_URL}/static/favicon.png"
									class=" size-6 -translate-x-1.5 rounded-full"
									alt="logo"
								/>
							</div>
							<div class=" self-center font-medium text-sm text-gray-850 dark:text-white">
								{$WEBUI_NAME}
							</div>
						</a>
					</div>

					<div
						class="self-start flex flex-none items-center space-x-0.5 md:space-x-1 text-gray-500 dark:text-gray-500"
					>
						<UserMenu
							className="max-w-[200px]"
							role={$user?.role}
							on:show={(e) => {
								if (e.detail === 'archived-chat') {
									showArchivedChats.set(true);
								}
							}}
						>
							<button
								class="select-none flex rounded-xl p-1.5 w-full hover:bg-gray-100 dark:hover:bg-gray-850 transition"
								aria-label="User Menu"
							>
								<div class=" self-center">
									<img
										src={$user?.profile_image_url}
										class="size-6 object-cover rounded-full"
										alt="User profile"
										draggable="false"
									/>
								</div>
							</button>
						</UserMenu>
					</div>
				</div>
			</nav>

			<div class="flex flex-col w-full min-h-screen max-h-screen items-center justify-center">
				<div class=" h-1/2 w-1/2 overflow-y-auto">
					<div class=" text-3xl font-semibold mb-3">Your Classes</div>

					<div class="flex w-full space-x-2 mb-2">
						<div
							class="flex flex-1 px-3 py-1.5 border dark:border-gray-600 outline-none rounded-lg"
						>
							<div class=" self-center ml-1 mr-3">
								<svg
									xmlns="http://www.w3.org/2000/svg"
									viewBox="0 0 20 20"
									fill="currentColor"
									class="w-4 h-4"
								>
									<path
										fill-rule="evenodd"
										d="M9 3.5a5.5 5.5 0 100 11 5.5 5.5 0 000-11zM2 9a7 7 0 1112.452 4.391l3.328 3.329a.75.75 0 11-1.06 1.06l-3.329-3.328A7 7 0 012 9z"
										clip-rule="evenodd"
									/>
								</svg>
							</div>
							<input
								class=" w-full text-sm pr-4 py-1 rounded-r-xl outline-none bg-transparent"
								bind:value={searchValue}
								placeholder={'Search Classes'}
							/>
						</div>
					</div>

					{#if !loading}
						<div class=" my-2 mb-5" id="class-list">
							{#each $classes.filter((c) => searchValue === '' || c.name
										.toLowerCase()
										.includes(searchValue.toLowerCase())) as class_}
								<div
									class=" flex space-x-4 cursor-pointer w-full px-3 py-2 dark:hover:bg-white/5 hover:bg-black/5 rounded-xl"
								>
									<div class=" flex flex-1 space-x-4 cursor-pointer w-full">
										<a href={`/classes/${encodeURIComponent(class_.id)}`}>
											<div class="flex items-center">
												<img
													src={class_.image_url ? class_.image_url : '/user.png'}
													alt="profile"
													class="rounded-full h-16 w-16 object-cover"
												/>
												<div class=" flex-1 self-center pl-5">
													<div class=" font-bold">{class_.name}</div>
													<div class="text-xs text-gray-400 dark:text-gray-500">
														Instructor: {class_.instructor_name}
													</div>
													<div class="text-xs text-gray-400 dark:text-gray-500">
														{assignedPromptLabel(class_.assigned_prompts)}
													</div>
												</div>
											</div></a
										>
									</div>
								</div>
							{:else}
								<div class="px-2">No classes found.</div>
							{/each}
						</div>
					{:else}
						<div class="px-2 flex items-center space-x-1">
							<svg
								class=" w-4 h-4"
								viewBox="0 0 24 24"
								fill="currentColor"
								xmlns="http://www.w3.org/2000/svg"
							>
								<style>
									.spinner_ajPY {
										transform-origin: center;
										animation: spinner_AtaB 0.75s infinite linear;
									}
									@keyframes spinner_AtaB {
										100% {
											transform: rotate(360deg);
										}
									}
								</style>
								<path
									d="M12,1A11,11,0,1,0,23,12,11,11,0,0,0,12,1Zm0,19a8,8,0,1,1,8-8A8,8,0,0,1,12,20Z"
									opacity=".25"
								/>
								<path
									d="M10.14,1.16a11,11,0,0,0-9,8.92A1.59,1.59,0,0,0,2.46,12,1.52,1.52,0,0,0,4.11,10.7a8,8,0,0,1,6.66-6.61A1.42,1.42,0,0,0,12,2.69h0A1.57,1.57,0,0,0,10.14,1.16Z"
									class="spinner_ajPY"
								/>
							</svg>
							<span>
								Loading...
							</span>
						</div>
					{/if}
				</div>
			</div>
		</div>
	</div>
</div>

<style>
	.loading {
		display: inline-block;
		clip-path: inset(0 1ch 0 0);
		animation: l 1s steps(3) infinite;
		letter-spacing: -0.5px;
	}

	@keyframes l {
		to {
			clip-path: inset(0 -1ch 0 0);
		}
	}

	pre[class*='language-'] {
		position: relative;
		overflow: auto;

		/* make space  */
		margin: 5px 0;
		padding: 1.75rem 0 1.75rem 1rem;
		border-radius: 10px;
	}

	pre[class*='language-'] button {
		position: absolute;
		top: 5px;
		right: 5px;

		font-size: 0.9rem;
		padding: 0.15rem;
		background-color: #828282;

		border: ridge 1px #7b7b7c;
		border-radius: 5px;
		text-shadow: #c4c4c4 0 0 2px;
	}

	pre[class*='language-'] button:hover {
		cursor: pointer;
		background-color: #bcbabb;
	}
</style>
