import Foundation
import UserNotifications

@main
struct OPCBlogNotifier {
    static func main() async {
        let args = Array(CommandLine.arguments.dropFirst())
        guard args.count >= 1 else { fail("Usage: OPCBlogNotifier status|send <id> <title> <body>|remove <id>") }
        let center = UNUserNotificationCenter.current()
        switch args[0] {
        case "status":
            let settings = await center.notificationSettings()
            print("bundle=\(Bundle.main.bundleIdentifier ?? "none") authorization=\(settings.authorizationStatus.rawValue)")
        case "send":
            guard args.count == 4 else { fail("send requires id, title and body") }
            do {
                guard try await center.requestAuthorization(options: [.alert, .sound]) else { fail("Notification permission denied") }
                let content = UNMutableNotificationContent()
                content.title = args[2]
                content.body = args[3]
                let request = UNNotificationRequest(identifier: args[1], content: content, trigger: nil)
                try await center.add(request)
                print("sent \(args[1])")
            } catch { fail("Notification failed: \(error)") }
        case "remove":
            guard args.count == 2 else { fail("remove requires id") }
            center.removePendingNotificationRequests(withIdentifiers: [args[1]])
            center.removeDeliveredNotifications(withIdentifiers: [args[1]])
            print("removed \(args[1])")
        default:
            fail("Unknown command")
        }
    }

    static func fail(_ message: String) -> Never {
        fputs("\(message)\n", stderr)
        exit(1)
    }
}
