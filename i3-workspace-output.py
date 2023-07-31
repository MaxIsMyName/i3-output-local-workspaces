#!/usr/bin/env python3
import i3ipc
import os
import sys
import argparse


def get_workspace_outer_number(workspace):
    try:
        return int(workspace.name.split(':')[-1].strip())
    except ValueError:
        return None
    

def get_output_workspace_offset(i3, output_offsets, output_name):
    if output_name not in output_offsets:
        sorted_outputs = sorted(filter(lambda x: x.active, i3.get_outputs()), key=lambda x: x.name)
        output_offsets[output_name] = (sorted_outputs.index(next(x for x in sorted_outputs if x.name == output_name)) * 100)

    return output_offsets[output_name]



def get_free_workspace_on_output(i3, output_name, try_number=-1):
    workspaces_on_current_output = [w for w in i3.get_workspaces() if w.output == output_name]

    if try_number == -1 or any(get_workspace_outer_number(w) == try_number for w in workspaces_on_current_output):
        max_number = max(get_workspace_outer_number(w) for w in workspaces_on_current_output)
        for workspace_num in range(1, max_number + 2):
            if all(get_workspace_outer_number(w) != workspace_num for w in workspaces_on_current_output):
                return workspace_num
    else:
        return try_number
    return None


def move_workspace(i3, output_offsets, args):
    workspaces = i3.get_workspaces()
    current_workspace = [w for w in workspaces if w.focused][0]
    current_output = current_workspace.output
    
    match args.direction:
        case 'up':
            sorted_outputs_y = sorted(list(filter((lambda x: x.active), i3.get_outputs())), key=(lambda x: x.rect.y))
            current_output_index = [x for (x, e) in enumerate(sorted_outputs_y) if e.name == current_output][0]
            target_output = sorted_outputs_y[current_output_index - 1].name

            new_workspace_num = get_free_workspace_on_output(target_output, get_workspace_outer_number(current_workspace))

            rename_command = f'rename workspace to "{get_output_workspace_offset(i3, output_offsets, target_output)+ new_workspace_num}: {new_workspace_num}"'
            command = f"move workspace to output {target_output}"
            if args.dry_run:
                print(command)
                print(rename_command)
            else:
                i3.command(rename_command)
                i3.command(command)

        case 'down':
            sorted_outputs_y = sorted(list(filter((lambda x: x.active), i3.get_outputs())), key=(lambda x: x.rect.y))
            current_output_index = [x for (x, e) in enumerate(sorted_outputs_y) if e.name == current_output][0]
            target_output_index = current_output_index + 1
            if target_output_index >= len(sorted_outputs_x):
                target_output_index = 0
            target_output = sorted_outputs_y[current_output_index + 1].name

            new_workspace_num = get_free_workspace_on_output(target_output, get_workspace_outer_number(current_workspace))

            rename_command = f'rename workspace to "{get_output_workspace_offset(i3, output_offsets, target_output)+ new_workspace_num}: {new_workspace_num}"'
            command = f"move workspace to output {target_output}"
            if args.dry_run:
                print(command)
                print(rename_command)
            else:
                i3.command(rename_command)
                i3.command(command)

        case 'left':
            sorted_outputs_x = sorted(list(filter((lambda x: x.active), i3.get_outputs())), key=(lambda x: x.rect.x))
            current_output_index = [x for (x, e) in enumerate(sorted_outputs_x) if e.name == current_output][0]
            target_output = sorted_outputs_x[current_output_index - 1].name

            new_workspace_num = get_free_workspace_on_output(i3, target_output, get_workspace_outer_number(current_workspace))

            rename_command = f'rename workspace to "{get_output_workspace_offset(i3, output_offsets, target_output)+ new_workspace_num}: {new_workspace_num}"'
            command = f"move workspace to output {target_output}"
            if args.dry_run:
                print(rename_command)
                print(command)
            else:
                i3.command(rename_command)
                i3.command(command)

        case 'right':
            sorted_outputs_x = sorted(list(filter((lambda x: x.active), i3.get_outputs())), key=(lambda x: x.rect.x))
            current_output_index = [x for (x, e) in enumerate(sorted_outputs_x) if e.name == current_output][0]
            target_output_index = current_output_index + 1
            if target_output_index >= len(sorted_outputs_x):
                target_output_index = 0
            target_output = sorted_outputs_x[current_output_index + 1].name

            new_workspace_num = get_free_workspace_on_output(i3, target_output, get_workspace_outer_number(current_workspace))

            rename_command = f'rename workspace to "{get_output_workspace_offset(i3, output_offsets, target_output)+ new_workspace_num}: {new_workspace_num}"'
            command = f"move workspace to output {target_output}"
            if args.dry_run:
                print(rename_command)
                print(command)
            else:
                i3.command(rename_command)
                i3.command(command)


def main():
    i3 = i3ipc.Connection()
    output_offsets = {}

    parser = argparse.ArgumentParser(description="Script to handle output local workspaces and containers.")
    subparsers = parser.add_subparsers(dest='command', help="command to send", required=True)

    move_workspace_parser = subparsers.add_parser('move_workspace', help="Move workspace")
    move_workspace_parser.add_argument("direction", choices=["left", "right", "up", "down"], help="Direction to move the workspace")

    move_container_parser = subparsers.add_parser("move_container", help="Move container")
    move_container_parser.add_argument("number", metavar="N", type=int, help="Workspace to move the container to")

    number_parser = subparsers.add_parser("number", help="Switch workspace")
    number_parser.add_argument("number", metavar="N", type=int, help="Switch workspace")

    parser.add_argument("-d", "--dry-run", help="print and do not run commands", action="store_true")
    args = parser.parse_args()

    offset = get_output_workspace_offset(i3, output_offsets, [w for w in i3.get_workspaces() if w.focused][0].output)

    match args.command:
        case 'number':
            # do_number(args.destination_workspace, args.dry_run)
            if args.dry_run:
                print(f'workspace {args.number + offset}: {args.number}')
            else:
                i3.command(f'workspace {args.number + offset}: {args.number}')
        case 'move_container':
            if args.dry_run:
                print(f'move container workspace "{args.number + offset}: {args.number}"')
            else:
                i3.command(f'move container workspace "{args.number + offset}: {args.number}"')
        case 'move_workspace':
            move_workspace(i3, output_offsets, args)

if __name__ == "__main__":
    main()
