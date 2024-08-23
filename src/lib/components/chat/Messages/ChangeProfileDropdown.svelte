<script lang="ts">
	import { chatId, classId, mobile, selectedPromptCommand } from "$lib/stores";
	import { flyAndScale } from "$lib/utils/transitions";
	import { DropdownMenu } from "bits-ui";

    export let show = false;
    export let profiles;
    export let selectedProfile;

	export let className = 'w-[16rem]';
</script>

<DropdownMenu.Root
    bind:open={show}
>
    <DropdownMenu.Trigger aria-label="add-student">
        <button class="text-sm ml-2 px-3 py-2 transition rounded-xl bg-gray-50 hover:bg-gray-100 dark:bg-gray-700 dark:hover:bg-gray-800"
            type="button"
        >
            <div class="self-center text-sm font-medium text-nowrap">Change Profile</div>
        </button>
    </DropdownMenu.Trigger>

    <DropdownMenu.Content
        class=" z-40 {$mobile
            ? `w-full`
            : `${className}`} max-w-[calc(100vw-1rem)] justify-start rounded-xl  bg-white dark:bg-gray-850 dark:text-white shadow-lg border border-gray-300/30 dark:border-gray-700/50  outline-none "
        transition={flyAndScale}
        side={$mobile ? 'bottom' : 'bottom-start'}
        sideOffset={4}
    >
        <slot>
            <div class="px-3 my-2 max-h-64 overflow-y-auto scrollbar-hidden">
                {#each profiles as profile}
                    <a
                        aria-label="item-item"
                        type="button"
                        class="flex w-full text-left font-medium line-clamp-1 select-none items-center rounded-button py-2 pl-3 pr-1.5 text-sm text-gray-700 dark:text-gray-100 outline-none transition-all duration-75 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg cursor-pointer data-[highlighted]:bg-muted"
                        href={`/c/?profile=${encodeURIComponent(profile.command)}`
										+ `&model=${profile.selected_model_id ? encodeURIComponent(profile.selected_model_id) : "gpt-4o"}`
										+ `&class=${$classId}`
                        }
                        on:click={() => {
                            $chatId = "";
                            selectedProfile = profile;
                            $selectedPromptCommand = profile.command;
                            show = false;
                        }}
                    >
                        <img
                            src={profile.image_url ? profile.image_url : '/user.png'}
                            alt="profile"
                            class="rounded-full h-8 w-8 object-cover"
                        />
                        <div class="flex items-center gap-2 ml-1">
                            <div class="">
                                {profile.title}
                            </div>
                        </div>
                    </a>
                {/each}
            </div>

            <div class="hidden w-[42rem]" />
            <div class="hidden w-[32rem]" />
        </slot>
    </DropdownMenu.Content>
</DropdownMenu.Root>