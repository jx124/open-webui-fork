<script lang="ts">
	import { getContext } from 'svelte';
	import { toast } from 'svelte-sonner';
	import { updateUserPassword } from '$lib/apis/auths';

	const i18n = getContext('i18n');

	let show = false;
	let currentPassword = '';
	let newPassword = '';
	let newPasswordConfirm = '';

	$: passwordsMatch = newPassword === newPasswordConfirm;
	$: validPassword = checkPassword(newPassword);

	const checkPassword = (str: string) => {
		if (str.length < 12) {
			return 'Password should have at least 12 characters.';
		} else if (str.length > 50) {
			return 'Password too long.';
		} else if (str.search(/\d/) == -1) {
			return 'Password should contain a number.';
		} else if (str.search(/[a-zA-Z]/) == -1) {
			return 'Password should contain a letter.';
		} else if (str.search(/[\!\@\#\$\%\^\&\*\(\)\_\+\,\.]/) == -1) {
			return 'Password should contain a symbol [!@#$%^&*()_+,.].';
		}
		return '';
	};

	const updatePasswordHandler = async () => {
		if (newPassword === newPasswordConfirm) {
			const res = await updateUserPassword(localStorage.token, currentPassword, newPassword).catch(
				(error) => {
					toast.error(error);
					return null;
				}
			);

			if (res) {
				toast.success($i18n.t('Successfully updated.'));
			}

			currentPassword = '';
			newPassword = '';
			newPasswordConfirm = '';
		} else {
			toast.error(
				`The passwords you entered don't quite match. Please double-check and try again.`
			);
			newPassword = '';
			newPasswordConfirm = '';
		}
	};
</script>

<form
	class="flex flex-col text-sm"
	on:submit|preventDefault={() => {
		updatePasswordHandler();
	}}
>
	<div class="flex justify-between items-center text-sm">
		<div class="  font-medium">{$i18n.t('Change Password')}</div>
		<button
			class=" text-xs font-medium text-gray-500"
			type="button"
			on:click={() => {
				show = !show;
			}}>{show ? $i18n.t('Hide') : $i18n.t('Show')}</button
		>
	</div>

	{#if show}
		<div class=" pt-2.5 space-y-1.5">
			<div class="flex flex-col w-full">
				<div class=" mb-1 text-xs text-gray-500">{$i18n.t('Current Password')}</div>

				<div class="flex-1">
					<input
						class="w-full rounded py-2 px-4 text-sm dark:text-gray-300 dark:bg-gray-800 outline-none"
						type="password"
						bind:value={currentPassword}
						autocomplete="current-password"
						required
					/>
				</div>
			</div>

			<div class="flex flex-col w-full">
				<div class=" mb-1 text-xs text-gray-500">{$i18n.t('New Password')}</div>

				<div class="flex-1">
					<input
						class={(validPassword === '' || newPassword === ''
						? 'border-transparent'
						: 'border-rose-500') + " w-full rounded py-2 px-4 text-sm dark:text-gray-300 dark:bg-gray-800 outline-none"}
						type="password"
						bind:value={newPassword}
						autocomplete="new-password"
						required
					/>
				</div>
			</div>

			{#if newPassword && validPassword !== ''}
				<div class="mt-1 text-xs text-rose-500">{validPassword}</div>
			{:else}
				<div class="mt-1 py-2" />
			{/if}

			<div class="flex flex-col w-full">
				<div class=" mb-1 text-xs text-gray-500">{$i18n.t('Confirm Password')}</div>

				<div class="flex-1">
					<input
						class={(passwordsMatch ? 'border-transparent' : 'border-rose-500')
							+ " w-full rounded py-2 px-4 text-sm dark:text-gray-300 dark:bg-gray-800 outline-none"}
						type="password"
						bind:value={newPasswordConfirm}
						autocomplete="off"
						required
					/>
				</div>
			</div>

			{#if !passwordsMatch}
				<div class="mt-1 text-xs text-rose-500">Passwords do not match.</div>
			{:else}
				<div class="mt-1 py-2" />
			{/if}
		</div>

		<div class="mt-1 flex justify-end">
			<button
				class=" px-4 py-2 text-xs bg-gray-800 hover:bg-gray-900 dark:bg-gray-700 dark:hover:bg-gray-800 
					text-gray-100 transition rounded-md font-medium disabled:pointer-events-none"
				disabled={!passwordsMatch || (validPassword !== "")}
			>
				{$i18n.t('Update password')}
			</button>
		</div>
	{/if}
</form>
