<script lang="ts">
	import { chats, classes, classId, prompts, WEBUI_NAME } from '$lib/stores';
	import { onMount } from 'svelte';
	import { getClassList } from '$lib/apis/classes';
	import { toast } from 'svelte-sonner';
	import { getPrompts } from '$lib/apis/prompts';
	import { getChatList } from '$lib/apis/chats';

	let loading = true;

	onMount(async () => {
		if ($classes.length === 0) {
            $classes = await getClassList(localStorage.token).catch((error) => toast.error(error));
        }
		if ($prompts.length === 0) {
            $prompts = await getPrompts(localStorage.token).catch((error) => toast.error(error));
        }
		if ($chats.length === 0) {
            $chats = await getChatList(localStorage.token).catch((error) => toast.error(error));
        }

        $classId = null;
		loading = false;
	});
</script>

<svelte:head>
	<title>
		Classes | {$WEBUI_NAME}
	</title>
</svelte:head>

<div class="flex flex-col w-full min-h-screen max-h-screen items-center justify-center">
    <div class=" h-1/2 w-1/2 overflow-y-auto">
        <div class=" text-3xl font-semibold mb-3">Your Classes</div>

        {#if !loading}
            <div class=" my-2 mb-5" id="class-list">
                {#each $classes as class_}
                    <div
                        class=" flex space-x-4 cursor-pointer w-full px-3 py-2 dark:hover:bg-white/5 hover:bg-black/5 rounded-xl"
                    >
                        <div class=" flex flex-1 space-x-4 cursor-pointer w-full">
                            <a href={`/classes/${encodeURIComponent(class_.id)}`}
                                on:click={() => {
                                    $classId = class_.id;
                                    localStorage.setItem("classId", $classId.toString());
                                }}>
                                <div class="flex items-center">
                                    <img
                                        src={class_.image_url ? class_.image_url : '/user.png'}
                                        alt="profile"
                                        class="rounded-full h-16 w-16 object-cover"
                                    />
                                    <div class=" flex-1 self-center pl-5">
                                        <div class=" font-bold">{class_.name}</div>
                                        <div class="text-xs text-gray-600 dark:text-gray-500">
                                            Instructor: {class_.instructor_name}
                                        </div>
                                        <div class="text-xs text-gray-600 dark:text-gray-500">
                                            Assignments: {class_.assignments.length}
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
