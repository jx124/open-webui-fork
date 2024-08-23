<script lang="ts">
	import { goto } from '$app/navigation';
	import { userResetEmail, userResetPassword, verifyUserOTP } from '$lib/apis/auths';
	import { WEBUI_BASE_URL } from '$lib/constants';
	import { WEBUI_NAME, user } from '$lib/stores';
	import { onMount, getContext } from 'svelte';
	import { toast } from 'svelte-sonner';

	const i18n = getContext('i18n');

	let loaded = false;
	let buttonLoading = false;

	let email = '';
	let OTP = '';
	let newPassword = '';
	let confirmPassword = '';

	$: passwordsMatch = newPassword === confirmPassword;
	$: validPassword = checkPassword(newPassword);
	$: resetButtonDisabled = !passwordsMatch || (validPassword !== '');

	let tab: 'email' | 'OTP' | 'password' = 'email';

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

	const resetPasswordHandler = async () => {
		buttonLoading = true;
		await userResetEmail(email).then(() => {
			toast.success('Reset password instructions sent');
			tab = 'OTP';
		});
		buttonLoading = false;
	};

	const verifyOTPHandler = async () => {
		buttonLoading = true;
		await verifyUserOTP(email, OTP)
			.then(() => {
				toast.success('OTP verified');
				tab = 'password';
			})
			.catch((err) => {
				toast.error(err);
			});
		buttonLoading = false;
	};

	const confirmResetHandler = async () => {
		buttonLoading = true;
		await userResetPassword(email, OTP, newPassword)
			.then(() => {
				toast.success('Successfully reset password');
				goto("/");
			})
			.catch((err) => {
				toast.error(err);
			});
		buttonLoading = false;
	};

	onMount(async () => {
		if ($user !== undefined) {
			await goto('/');
		}
		loaded = true;
	});
</script>

<svelte:head>
	<title>
		{`${$WEBUI_NAME}`}
	</title>
</svelte:head>

{#if loaded}
	<div class="fixed m-10 z-50">
		<div class="flex space-x-2">
			<div class=" self-center">
				<img
					crossorigin="anonymous"
					src="{WEBUI_BASE_URL}/static/favicon.png"
					class=" w-8 rounded-full"
					alt="logo"
				/>
			</div>
		</div>
	</div>

	<div class=" bg-white dark:bg-gray-950 min-h-screen w-full flex justify-center font-mona">
		<div class="w-full sm:max-w-md px-10 min-h-screen flex flex-col text-center">
			{#if tab === 'email'}
				<div class="  my-auto pb-10 w-full dark:text-gray-100">
					<form
						class=" flex flex-col justify-center"
						on:submit|preventDefault={() => {
							resetPasswordHandler();
						}}
					>
						<div class="mb-1">
							<div class=" text-2xl font-bold">Reset Password</div>
						</div>

						<div class="flex flex-col mt-4">
							<div class=" text-sm font-semibold text-left mb-1">{$i18n.t('Email')}</div>
							<input
								bind:value={email}
								type="email"
								class=" px-5 py-3 rounded-2xl w-full text-sm outline-none border dark:border-none dark:bg-gray-900"
								autocomplete="email"
								placeholder={$i18n.t('Enter Your Account Email')}
								required
							/>
						</div>

						<div class="mt-5">
							<button
								class=" bg-gray-900 hover:bg-gray-800 w-full rounded-2xl text-white font-semibold text-sm py-3 transition"
								type="submit"
							>
								{#if buttonLoading}
									<div class="px-2 flex items-center justify-center space-x-1">
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
										<span> Loading... </span>
									</div>
								{:else}
									Reset Password
								{/if}
							</button>
						</div>
					</form>
				</div>
			{:else if tab === 'OTP'}
				<div class="  my-auto pb-10 w-full dark:text-gray-100">
					<form
						class=" flex flex-col justify-center"
						on:submit|preventDefault={() => {
							verifyOTPHandler();
						}}
					>
						<div class="mb-1">
							<div class=" text-2xl font-bold">Enter Your OTP</div>
						</div>

						<div class="flex flex-col mt-4">
							<div class=" text-sm font-semibold text-left mb-1">OTP</div>
							<input
								bind:value={OTP}
								type="text"
								class=" px-5 py-3 rounded-2xl w-full text-sm outline-none border dark:border-none dark:bg-gray-900"
								placeholder={$i18n.t('Enter Your 6-Digit OTP')}
								autocomplete="one-time-code"
								required
							/>
						</div>

						<div class="mt-5">
							<button
								class=" bg-gray-900 hover:bg-gray-800 w-full rounded-2xl text-white font-semibold text-sm py-3 transition"
								type="submit"
							>
								{#if buttonLoading}
									<div class="px-2 flex items-center justify-center space-x-1">
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
										<span> Loading... </span>
									</div>
								{:else}
									Verify
								{/if}
							</button>
						</div>

						<div class=" mt-1 text-sm text-center">
							Please check your spam folder.<br />
							The OTP expires in 15 minutes.
						</div>

						<div class=" mt-1 text-sm text-center font-medium">
							<button
								type="button"
								class="underline"
								on:click={() => {
									tab = 'email';
								}}
							>
								Re-enter Email
							</button>
						</div>
					</form>
				</div>
			{:else}
				<div class="  my-auto pb-10 w-full dark:text-gray-100">
					<form
						class=" flex flex-col justify-center"
						on:submit|preventDefault={() => {
							confirmResetHandler();
						}}
					>
						<div class="mb-1">
							<div class=" text-2xl font-bold">Enter New Password</div>
						</div>

						<div class="flex flex-col mt-4">
							<div class=" text-sm font-semibold text-left mb-1">New Password</div>
							<input
								bind:value={newPassword}
								type="password"
								class={(validPassword === '' || newPassword === ''
									? 'border-transparent'
									: 'border-rose-500') +
									' px-5 py-3 rounded-2xl w-full text-sm outline-none border dark:bg-gray-900'}
								placeholder={$i18n.t('Enter Your New Password')}
								autocomplete="new-password"
								required
							/>
						</div>

						{#if newPassword && validPassword !== ''}
							<div class="mt-1 text-sm text-rose-500">{validPassword}</div>
						{:else}
							<div class="mt-1 py-2.5" />
						{/if}

						<div class="flex flex-col">
							<div class=" text-sm font-semibold text-left mb-1">Confirm Password</div>
							<input
								bind:value={confirmPassword}
								type="password"
								class={(passwordsMatch ? 'border-transparent' : 'border-rose-500') +
									' px-5 py-3 rounded-2xl w-full text-sm outline-none border dark:bg-gray-900'}
								placeholder={$i18n.t('Confirm Your New Password')}
								autocomplete="new-password"
								required
							/>
						</div>

						{#if !passwordsMatch}
							<div class="mt-1 text-sm text-rose-500">Passwords do not match.</div>
						{:else}
							<div class="mt-1 py-2.5" />
						{/if}

						<div class="mt-3">
							<button
								class="bg-gray-900 hover:bg-gray-800 w-full rounded-2xl text-white font-semibold 
										text-sm py-3 transition disabled:text-gray-600 disabled:pointer-events-none"
								type="submit"
								disabled={resetButtonDisabled}
							>
								{#if buttonLoading}
									<div class="px-2 flex items-center justify-center space-x-1">
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
										<span> Loading... </span>
									</div>
								{:else}
									Reset Password
								{/if}
							</button>
						</div>
					</form>
				</div>
			{/if}
		</div>
	</div>
{/if}

<style>
	.font-mona {
		font-family: 'Mona Sans', -apple-system, 'Arimo', ui-sans-serif, system-ui, 'Segoe UI', Roboto,
			Ubuntu, Cantarell, 'Noto Sans', sans-serif, 'Helvetica Neue', Arial, 'Apple Color Emoji',
			'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji';
	}
</style>
