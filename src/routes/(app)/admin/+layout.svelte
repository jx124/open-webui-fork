<script lang="ts">
	import { onMount, getContext } from 'svelte';

	import { WEBUI_NAME, showSidebar, user } from '$lib/stores';
	import MenuLines from '$lib/components/icons/MenuLines.svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';

	const i18n = getContext('i18n');

	onMount(async () => {
		if ($user?.role === "instructor") {
			const restricted = ["/(app)/admin/evaluations", "/(app)/admin/documents", "/(app)/admin/playground"];
			
			for (const route of restricted) {
				if ($page.route.id?.startsWith(route)) {
					await goto("/admin");
				}
			}
		}
	})
</script>

<svelte:head>
	<title>
		Admin Panel | {$WEBUI_NAME}
	</title>
</svelte:head>

<div class=" flex flex-col w-full min-h-screen max-h-screen">
	<div class=" px-4 pt-3 mt-0.5 mb-1">
		<div class=" flex items-center gap-1">
			<div class=" mr-1 self-start flex flex-none items-center">
				<button
					id="sidebar-toggle-button"
					class="cursor-pointer p-1 flex rounded-xl hover:bg-gray-100 dark:hover:bg-gray-850 transition"
					on:click={() => {
						showSidebar.set(!$showSidebar);
					}}
				>
					<div class=" m-auto self-center">
						<MenuLines />
					</div>
				</button>
			</div>
			<div class="flex items-center text-xl font-semibold">Admin Panel</div>
		</div>
	</div>

	<div class="px-4 my-1">
		<div
			class="flex scrollbar-none overflow-x-auto w-fit text-center text-sm font-medium rounded-xl bg-transparent/10 p-1"
		>
			<a
				class="min-w-fit rounded-lg p-1.5 px-3 {$page.url.pathname.includes('/admin/classes')
					? 'bg-gray-50 dark:bg-gray-850'
					: ''} transition"
				href="/admin/classes">{$i18n.t('Classes')}</a
			>

			<a
				class="min-w-fit rounded-lg p-1.5 px-3 {$page.url.pathname.includes('/admin/profiles')
					? 'bg-gray-50 dark:bg-gray-850'
					: ''} transition"
				href="/admin/profiles">{$i18n.t('Profiles')}</a
			>

			<a
				class="min-w-fit rounded-lg p-1.5 px-3 {$page.url.pathname.includes('/admin/models')
					? 'bg-gray-50 dark:bg-gray-850'
					: ''} transition"
				href="/admin/models">{$i18n.t('Models')}</a
			>
			
			{#if $user?.role === "admin"}
				<a
					class="min-w-fit rounded-lg p-1.5 px-3 {$page.url.pathname.includes('/admin/evaluations')
						? 'bg-gray-50 dark:bg-gray-850'
						: ''} transition"
					href="/admin/evaluations">{$i18n.t('Evaluations')}</a
				>
			{/if}

			<a
				class="min-w-fit rounded-lg p-1.5 px-3 {$page.url.pathname.includes('/admin/users')
					? 'bg-gray-50 dark:bg-gray-850'
					: ''} transition"
				href="/admin/users">{$i18n.t('Users')}</a
			>

			<a
				class="min-w-fit rounded-lg p-1.5 px-3 {$page.url.pathname.includes('/admin/assignments')
					? 'bg-gray-50 dark:bg-gray-850'
					: ''} transition"
				href="/admin/assignments">{$i18n.t('Assignments')}</a
			>

			{#if $user?.role === "admin"}
                <a
                    class="min-w-fit rounded-lg p-1.5 px-3 {$page.url.pathname.includes('/admin/metrics')
                        ? 'bg-gray-50 dark:bg-gray-850'
                        : ''} transition"
                    href="/admin/metrics">{$i18n.t('Metrics')}</a
                >
            {/if}

			{#if false}
				<a
					class="min-w-fit rounded-lg p-1.5 px-3 {$page.url.pathname.includes('/admin/documents')
						? 'bg-gray-50 dark:bg-gray-850'
						: ''} transition"
					href="/admin/documents"
				>
					{$i18n.t('Documents')}
				</a>

				<a
					class="min-w-fit rounded-lg p-1.5 px-3 {$page.url.pathname.includes('/admin/playground')
						? 'bg-gray-50 dark:bg-gray-850'
						: ''} transition"
					href="/admin/playground">{$i18n.t('Playground')}</a
				>
			{/if}
		</div>
	</div>

	<hr class=" my-2 dark:border-gray-850" />

	<div class=" py-1 px-5 flex-1 max-h-full overflow-y-auto">
		<slot />
	</div>
</div>
