<script lang="ts">
	import { chats, classes, classId, showArchivedChats, showSettings, user, WEBUI_NAME } from '$lib/stores';
	import { toast } from 'svelte-sonner';
	import SettingsModal from '$lib/components/chat/SettingsModal.svelte';
	import ArchivedChatsModal from '$lib/components/layout/Sidebar/ArchivedChatsModal.svelte';
	import { getChatList } from '$lib/apis/chats';
	import Navbar from '$lib/components/layout/Navbar.svelte';
	import Sidebar from '$lib/components/layout/Sidebar.svelte';
	import { onMount } from 'svelte';

	let className: string = "";

    $: className = $classes.find((c) => c.id === $classId)?.name ?? "";
    onMount(() => {
	    className = $classes.find((c) => c.id === $classId)?.name ?? "";
    })
</script>

<svelte:head>
	<title>
		Classes | {$WEBUI_NAME}
	</title>
</svelte:head>

<SettingsModal bind:show={$showSettings} />
<ArchivedChatsModal
	bind:show={$showArchivedChats}
	on:change={async () => {
		$chats = await getChatList(localStorage.token).catch((error) => toast.error(error));
	}}
/>

<div class="app relative">
	<div class=" text-gray-700 dark:text-gray-100 bg-white dark:bg-gray-900 min-h-screen overflow-auto flex flex-row" >
        {#if className}
            <Sidebar />
        {/if}
		<div class="min-h-[calc(100dvh)] max-h-[calc(100dvh)] w-full max-w-full flex flex-col">
            <Navbar 
                isSubmitted={false}
                chat={undefined}
            />
            <slot />
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
